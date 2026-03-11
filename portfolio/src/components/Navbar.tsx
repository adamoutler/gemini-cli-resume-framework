'use client';

import { TreeNode } from "@/lib/api"; // Ensure this matches your API path
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState, useRef, useEffect } from "react";
import { ChevronDown, Menu, X } from "lucide-react";

// Recursive Dropdown Item
const NavDropdown = ({ node }: { node: TreeNode }) => {
    const [isOpen, setIsOpen] = useState(false);
    const dropdownRef = useRef<HTMLDivElement>(null);
    const pathname = usePathname();
    const isActive = pathname.startsWith(node.path);

    // Close when clicking outside
    useEffect(() => {
        function handleClickOutside(event: MouseEvent) {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
                setIsOpen(false);
            }
        }
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    return (
        <div className="relative group" ref={dropdownRef}>
            <button
                onClick={() => setIsOpen(!isOpen)}
                className={`flex items-center gap-1 font-medium transition-colors hover:text-primary ${isActive ? 'text-primary' : 'text-gray-300'}`}
            >
                {node.name}
                <ChevronDown size={14} className={`transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`} />
            </button>

            {/* Dropdown Menu */}
            {(isOpen || false) && (
                <div className="absolute top-full left-0 mt-2 w-64 bg-[#0a0a0a] border border-white/10 rounded-lg shadow-xl z-50 overflow-hidden flex flex-col">
                    {node.children?.map(child => (
                        child.type === 'file' ? (
                            <Link
                                key={child.path}
                                href={child.path}
                                onClick={() => setIsOpen(false)}
                                className="block px-4 py-2 text-sm text-gray-300 hover:bg-white/5 hover:text-white truncate"
                            >
                                {child.name}
                            </Link>
                        ) : (
                            // Nested Dropdown (simplified as a group header for now, or link to folder index)
                            <Link
                                key={child.path}
                                href={child.path}
                                onClick={() => setIsOpen(false)}
                                className="block px-4 py-2 text-sm font-semibold text-yellow-500/80 hover:bg-white/5 truncate border-t border-white/5 first:border-0"
                            >
                                📂 {child.name}
                            </Link>
                        )
                    ))}
                </div>
            )}
        </div>
    );
};

export default function Navbar({ tree }: { tree: TreeNode[] }) {
    const [isMobileOpen, setIsMobileOpen] = useState(false);

    return (
        <nav className="sticky top-0 z-50 w-full backdrop-blur-md bg-black/50 border-b border-white/10">
            <div className="container mx-auto px-4 h-16 flex items-center justify-between">
                {/* Logo / Brand */}
                <Link href="/" className="text-xl font-bold gradient-text tracking-tight hover:opacity-80 transition-opacity">
                    [Your Name]
                </Link>

                {/* Desktop Nav */}
                <div className="hidden md:flex items-center gap-8">
                    {tree.map(node => (
                        node.type === 'folder' ? (
                            <NavDropdown key={node.path} node={node} />
                        ) : (
                            <Link
                                key={node.path}
                                href={node.path}
                                className="text-gray-300 hover:text-primary transition-colors font-medium"
                            >
                                {node.name}
                            </Link>
                        )
                    ))}
                </div>

                {/* Mobile Menu Button */}
                <button
                    className="md:hidden text-gray-300 hover:text-white"
                    onClick={() => setIsMobileOpen(!isMobileOpen)}
                >
                    {isMobileOpen ? <X size={24} /> : <Menu size={24} />}
                </button>
            </div>

            {/* Mobile Nav Overlay */}
            {isMobileOpen && (
                <div className="md:hidden absolute top-16 left-0 w-full bg-[#0a0a0a] border-b border-white/10 shadow-xl p-4 flex flex-col gap-4">
                    {tree.map(node => (
                        <div key={node.path} className="flex flex-col gap-2">
                            {node.type === 'folder' ? (
                                <>
                                    <div className="font-semibold text-gray-400 uppercase text-xs tracking-wider">{node.name}</div>
                                    <div className="pl-4 flex flex-col gap-2 border-l border-white/10">
                                        {node.children?.map(child => (
                                            <Link
                                                key={child.path}
                                                href={child.path}
                                                onClick={() => setIsMobileOpen(false)}
                                                className="text-sm text-gray-300 hover:text-white"
                                            >
                                                {child.name}
                                            </Link>
                                        ))}
                                    </div>
                                </>
                            ) : (
                                <Link
                                    href={node.path}
                                    onClick={() => setIsMobileOpen(false)}
                                    className="font-medium text-gray-200 hover:text-primary"
                                >
                                    {node.name}
                                </Link>
                            )}
                        </div>
                    ))}
                </div>
            )}
        </nav>
    );
}
