import Link from 'next/link';
import { TreeNode } from '@/lib/api';
import { Folder, FileText, ChevronRight } from 'lucide-react';

export default function FolderIndex({ title, items }: { title: string, items: TreeNode[] }) {

    // Group items by 'type' frontmatter if available
    const groupedItems: Record<string, TreeNode[]> = { 'General': [] };

    items.forEach(item => {
        const type = (item.frontmatter?.type as string) || 'General';
        if (!groupedItems[type]) groupedItems[type] = [];
        groupedItems[type].push(item);
    });

    const sortedGroups = Object.keys(groupedItems).sort((a, b) => {
        if (a === 'General') return 1; // General at bottom
        if (b === 'General') return -1;
        return a.localeCompare(b);
    });

    return (
        <div className="container mx-auto px-4 py-12 max-w-5xl">
            <h1 className="text-4xl font-bold mb-8 gradient-text">{title}</h1>

            {sortedGroups.map(group => {
                const groupItems = groupedItems[group];
                if (groupItems.length === 0) return null;

                return (
                    <div key={group} className="mb-12">
                        {group !== 'General' && (
                            <h2 className="text-xl font-semibold text-gray-300 mb-4 border-b border-white/10 pb-2 capitalize">{group}</h2>
                        )}

                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            {groupItems.map((item) => {
                                // Check for icon in frontmatter
                                const iconChar = item.frontmatter?.icon as string | undefined;

                                return (
                                    <Link
                                        key={item.path}
                                        href={item.path}
                                        className="group glass-panel p-4 flex items-center gap-4 hover:bg-white/5 transition-all duration-300 border border-white/5 hover:border-primary/30"
                                    >
                                        <div className={`p-3 rounded-lg flex items-center justify-center w-12 h-12 text-xl ${item.type === 'folder'
                                                ? 'bg-blue-500/10 text-blue-400'
                                                : 'bg-purple-500/10 text-purple-400'
                                            }`}>
                                            {iconChar ? (
                                                <span>{iconChar}</span>
                                            ) : (
                                                item.type === 'folder' ? <Folder size={24} /> : <FileText size={24} />
                                            )}
                                        </div>

                                        <div className="flex-1 min-w-0">
                                            <h3 className="font-semibold text-gray-200 truncate group-hover:text-white transition-colors">
                                                {(item.frontmatter?.title as string) || item.name}
                                            </h3>
                                            <p className="text-xs text-secondary truncate">
                                                {(item.frontmatter?.summary as string) || (item.type === 'folder' ? 'Folder' : 'Document')}
                                            </p>
                                        </div>

                                        <ChevronRight size={16} className="text-gray-600 group-hover:text-primary transition-colors opacity-0 group-hover:opacity-100" />
                                    </Link>
                                );
                            })}
                        </div>
                    </div>
                );
            })}
        </div>
    );
}
