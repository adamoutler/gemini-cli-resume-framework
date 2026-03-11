import { getTree } from "@/lib/api";
import FolderIndex from "@/components/FolderIndex";

export default function Home() {
  const tree = getTree();
  return <FolderIndex title="Portfolio Dashboard" items={tree} />;
}
