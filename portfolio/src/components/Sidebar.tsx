'use client';
import { TreeNode } from "@/lib/api";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { ChevronRight, ChevronDown, FileText, Folder } from "lucide-react";

const SidebarNode = ({ node, level = 0 }: { node: TreeNode, level?: number }) => {
    const [isOpen, setIsOpen] = useState(level === 0);
    const pathname = usePathname();
    const isFile = node.type === 'file';

    const isActive = pathname === node.path;

    if (isFile) {
        return (
            <Link
                href={node.path}
                className={`flex items-center gap-2 py-1.5 px-2 rounded-md transition-colors text-sm ${isActive
                        ? 'bg-primary/20 text-primary font-medium'
                        : 'text-gray-400 hover:text-white hover:bg-white/5'
                    }`}
                style={{ paddingLeft: `${level * 12 + 8}px` }}
            >
                <FileText size={14} className="min-w-[14px]" />
                <span className="truncate">{node.name}</span>
            </Link>
        );
    }

    return (
        <div>
            <div
                onClick={() => setIsOpen(!isOpen)}
                className={`flex items-center gap-2 py-1.5 px-2 rounded-md hover:bg-white/5 cursor-pointer text-sm font-semibold w-full select-none ${isOpen ? 'text-white' : 'text-gray-400'}`}
                style={{ paddingLeft: `${level * 12 + 8}px` }}
            >
                <span className="min-w-[14px] flex justify-center">
                    {isOpen ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
                </span>
                <Folder size={14} className={`min-w-[14px] ${isOpen ? 'text-yellow-500' : 'text-yellow-500/60'}`} />
                <span className="truncate capitalize">{node.name}</span>
            </div>

            {isOpen && node.children && (
                <div className="flex flex-col border-l border-white/5 ml-[15px] mt-1 space-y-0.5">
                    {node.children.map((child) => (
                        <SidebarNode key={child.path} node={child} level={level + 1} />
                    ))}
                </div>
            )}
        </div>
    );
};

export default function Sidebar({ tree }: { tree: TreeNode[] }) {
    return (
        <aside className="w-80 h-screen sticky top-0 bg-[#0a0a0a] border-r border-white/10 overflow-y-auto hidden md:flex flex-col scrollbar-thin scrollbar-thumb-white/10">
            <div className="p-6 border-b border-white/10">
                <Link href="/" className="text-xl font-bold gradient-text tracking-tight flex items-center gap-2">
                    Portfolio
                </Link>
                <p className="text-xs text-secondary mt-2">Content Explorer</p>
            </div>

            <nav className="flex-1 p-4 space-y-1">
                {tree.map((node) => (
                    <SidebarNode key={node.path} node={node} />
                ))}
            </nav>
        </aside>
    );
}
