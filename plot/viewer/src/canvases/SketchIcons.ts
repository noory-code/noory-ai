import {
  Bell,
  Box,
  Briefcase,
  ClipboardList,
  Clock,
  Database,
  DollarSign,
  Flag,
  Folder,
  Globe,
  Heart,
  Key,
  type LucideIcon,
  Lock,
  Map,
  MessageCircle,
  Package,
  Settings,
  Shield,
  ShoppingCart,
  Star,
  Tag,
  Target,
  Wrench,
  User,
  Users,
  Zap,
} from "lucide-react";

/**
 * Curated icon palette shown in the body modal. The key is stored in
 * `node.icon` and serialised to the sketch JSON; the value is the Lucide
 * component reference used at render time.
 */
export const ICON_MAP: Record<string, LucideIcon> = {
  user: User,
  users: Users,
  briefcase: Briefcase,
  "dollar-sign": DollarSign,
  star: Star,
  clock: Clock,
  tag: Tag,
  flag: Flag,
  heart: Heart,
  shield: Shield,
  zap: Zap,
  box: Box,
  package: Package,
  folder: Folder,
  tool: Wrench,
  target: Target,
  "message-circle": MessageCircle,
  globe: Globe,
  map: Map,
  settings: Settings,
  lock: Lock,
  key: Key,
  bell: Bell,
  "shopping-cart": ShoppingCart,
  database: Database,
  "clipboard-list": ClipboardList,
};

export const ICON_KEYS: readonly string[] = Object.keys(ICON_MAP);

export function getIcon(name: string | null | undefined): LucideIcon | null {
  if (!name) return null;
  return ICON_MAP[name] ?? null;
}
