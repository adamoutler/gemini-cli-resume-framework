import { getItemBySlug, getTree, TreeNode } from '@/lib/api';
import { notFound } from 'next/navigation'; // Correct import for App Router
import FolderIndex from '@/components/FolderIndex';
import DocView from '@/components/DocView';

// Generate static params for ALL nodes in the tree
export async function generateStaticParams() {
    const tree = getTree();
    const params: { slug: string[] }[] = [];

    function traverse(nodes: TreeNode[]) {
        for (const node of nodes) {
            params.push({ slug: node.slug });
            if (node.children) {
                traverse(node.children);
            }
        }
    }
    traverse(tree);
    return params;
}

export default async function Page({ params }: { params: Promise<{ slug: string[] }> }) {
    const { slug } = await params;
    const item = getItemBySlug(slug);

    if (!item) {
        notFound();
    }

    if (item.type === 'folder') {
        return <FolderIndex title={item.name} items={item.children || []} />;
    } else {
        return <DocView node={item} />;
    }
}
