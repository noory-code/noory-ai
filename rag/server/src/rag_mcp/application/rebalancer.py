"""Rebalance use case.

`prep` surfaces candidates for the calling Claude to judge:

- ``alias_candidates``  : entity pairs whose names are case-insensitively equal
                           but have distinct ids — usually safe to merge.
- ``communities``        : freshly detected community assignments. Claude may
                           write a summary for any community lacking one.

`commit` applies the judgments back to the graph: entity merges (repoint
MENTIONS and RELATED edges onto the kept entity — preserving rel type,
weight, and direction — then drop the duplicate node) and community
summaries.

Note: detection of near-duplicate *chunks* is deferred to a future revision.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ..domain.models import EntityRow
from ..domain.ports import CommunityDetectorPort, GraphIndexPort


@dataclass(frozen=True)
class AliasCandidate:
    keep_id: str
    drop_id: str
    name: str


@dataclass(frozen=True)
class CommunityInfo:
    community_id: int
    member_ids: list[str]
    needs_summary: bool


@dataclass
class RebalancePrep:
    alias_candidates: list[AliasCandidate] = field(default_factory=list)
    communities: list[CommunityInfo] = field(default_factory=list)


@dataclass(frozen=True)
class MergeDecision:
    keep_id: str
    drop_id: str


@dataclass(frozen=True)
class SummaryDecision:
    community_id: int
    summary: str          # short topic label or paragraph
    member_summary: dict[str, str] = field(default_factory=dict)  # per-entity overrides


@dataclass(frozen=True)
class CommitResult:
    merged: int
    summaries_applied: int


class Rebalancer:
    def __init__(
        self,
        *,
        graph: GraphIndexPort,
        community: CommunityDetectorPort,
    ):
        self.graph = graph
        self.community = community

    # ----------------------------------------------------------------- prep

    def prep(self) -> RebalancePrep:
        entities = self.graph.list_entities()
        aliases = self._alias_candidates(entities)

        ids = [e.id for e in entities]
        edges = self.graph.all_edges()
        membership = self.community.detect(ids, edges)
        for eid, cid in membership.items():
            self.graph.set_community(eid, cid)

        by_community: dict[int, list[str]] = {}
        for eid, cid in membership.items():
            by_community.setdefault(cid, []).append(eid)

        # An entity is considered "needs summary" if any member of its community
        # has an empty summary. We surface one info per community.
        summary_present = {e.id: bool(e.summary.strip()) for e in entities}
        communities = [
            CommunityInfo(
                community_id=cid,
                member_ids=sorted(members),
                needs_summary=any(not summary_present.get(m, False) for m in members),
            )
            for cid, members in sorted(by_community.items())
        ]
        return RebalancePrep(alias_candidates=aliases, communities=communities)

    @staticmethod
    def _alias_candidates(entities: list[EntityRow]) -> list[AliasCandidate]:
        buckets: dict[str, list[EntityRow]] = {}
        for e in entities:
            key = e.name.strip().lower()
            if not key:
                continue
            buckets.setdefault(key, []).append(e)
        candidates: list[AliasCandidate] = []
        for group in buckets.values():
            if len(group) < 2:
                continue
            # Stable choice: keep the lexicographically smaller id, drop the others.
            sorted_group = sorted(group, key=lambda x: x.id)
            keeper = sorted_group[0]
            for other in sorted_group[1:]:
                candidates.append(
                    AliasCandidate(keep_id=keeper.id, drop_id=other.id, name=keeper.name)
                )
        return candidates

    # ----------------------------------------------------------------- commit

    def commit(
        self,
        merges: list[MergeDecision],
        summaries: list[SummaryDecision],
    ) -> CommitResult:
        merged = 0
        for m in merges:
            if m.keep_id == m.drop_id:
                continue
            self._merge_entities(m.keep_id, m.drop_id)
            merged += 1

        applied = 0
        for s in summaries:
            for entity_id, txt in s.member_summary.items():
                self.graph.set_summary(entity_id, txt)
            if s.summary:
                # Apply community-level summary to every member of the community.
                members = [
                    e.id for e in self.graph.list_entities(community_id=s.community_id)
                ]
                for m_id in members:
                    if m_id in s.member_summary:
                        continue
                    self.graph.set_summary(m_id, s.summary)
            applied += 1

        return CommitResult(merged=merged, summaries_applied=applied)

    def _merge_entities(self, keep_id: str, drop_id: str) -> None:
        """Fold ``drop_id`` into ``keep_id`` without losing graph data.

        - MENTIONS: every chunk that mentioned drop is repointed to keep.
          ``mention`` is a MERGE, so a chunk that already mentions keep is
          deduplicated rather than doubled.
        - RELATED: every relation incident to drop is repointed to keep,
          preserving rel type, weight, and direction. Repointed self-loops
          (keep -> keep) are discarded. When a repointed edge collides with
          an existing (src, rel_type, dst), the higher weight wins (on a
          tie the existing edge is kept as-is).
        - Finally the drop node is deleted; its now-stale edges detach
          with it.
        """
        for chunk_id in self.graph.chunks_mentioning(drop_id):
            self.graph.mention(chunk_id, keep_id)

        existing: dict[tuple[str, str, str], float] = {
            (src, rtype, dst): weight
            for src, dst, rtype, weight in self.graph.relations_of(keep_id)
        }
        for src, dst, rtype, weight in self.graph.relations_of(drop_id):
            new_src = keep_id if src == drop_id else src
            new_dst = keep_id if dst == drop_id else dst
            if new_src == new_dst:
                continue
            key = (new_src, rtype, new_dst)
            prior = existing.get(key)
            if prior is not None and prior >= weight:
                continue
            self.graph.relate(new_src, new_dst, rtype=rtype, weight=weight)
            existing[key] = weight

        self.graph.delete_entity(drop_id)
