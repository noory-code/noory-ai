/**
 * ServiceDetail-canvas wrapper.
 *
 * v0.15 Phase 3.4 (initial): hid the root-service node + suppressed
 * the synthetic anchor on the grounds that the modal header already
 * named the service.
 *
 * v0.27.3 (D-2026-05-26-G): the canvas's *subject* is the service.
 * The root-service node was made **visible** at the centre as the
 * design subject + BFS root for tree auto-layout.
 *
 * v0.27.11 (D-2026-05-28-B): partial revert of D-2026-05-26-G —
 * per the user's 2026-05-28 ServiceDetail design statement, the
 * canvas content is **actor / interaction / value / upper-link**
 * peers and edges between them; the service itself is the
 * **implicit** subject named by the modal header. Showing the
 * service as a centre node was reading as duplication ("로그인
 * 서비스인데 로그인 노드가 들어있는 것도 이상하고" — user,
 * 2026-05-28). The root-service stays in ``doc.service_ref`` (so
 * `service_detail/<id>/detail.json` keeps its identity), but the
 * canvas hides it. The tree auto-layout still uses the hidden
 * service_ref as the BFS hub — that part of D-2026-05-26-G stays.
 *
 * D-2026-06-15-L — actor_ref is NOT drillable here: clicking a
 * user/actor opens its inspector (per-service motivation/pain, D-2026-06-15-J)
 * and never navigates away to the Actors canvas. (The old double-click
 * jump-to-master was unwanted; reach the master via the Actors tab.)
 */
import { SketchCanvas, type SketchCanvasProps } from "./SketchCanvas";

export function ServiceDetailCanvas(props: SketchCanvasProps) {
  return (
    <SketchCanvas
      {...props}
      hideRootServiceNode={true}
      showFoldButton={true}
      injectAnchor={false}
      layoutAlgo="tree"
      showDirectionSwitch={true}
    />
  );
}
