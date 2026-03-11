import { TreeNode } from '@/lib/api';
import { remark } from 'remark';
import html from 'remark-html';
import { ArrowLeft, ExternalLink, Github } from 'lucide-react';
import Link from 'next/link';

export default async function DocView({ node }: { node: TreeNode }) {
    if (!node.content) return null;

    const processedContent = await remark()
        .use(html)
        .process(node.content);
    const contentHtml = processedContent.toString();

    const tags = (node.frontmatter?.keywords as string[]) || (node.frontmatter?.tags as string[]) || [];
    const url = node.frontmatter?.url as string | undefined;
    const repo = (node.frontmatter?.repo || node.frontmatter?.github) as string | undefined;

    // Logic: Use title if present, otherwise use summary as title. 
    // If title is used, summary becomes description.
    let title = node.frontmatter?.title as string | undefined;
    let summary = node.frontmatter?.summary as string | undefined;

    if (!title && summary) {
        title = summary; // Promote summary to title
        summary = undefined; // Clear summary so it doesn't repeat
    } else if (!title && !summary) {
        title = node.name; // Fallback to filename/slug
    }

    const icon = node.frontmatter?.icon as string | undefined;

    return (
        <article className="min-h-screen py-12 px-4 md:px-0">
            <div className="container mx-auto px-4 max-w-3xl">
                <header className="mb-12 pb-8 border-b border-white/10">
                    <div className="flex items-center gap-4 mb-6">
                        {icon && <span className="text-4xl">{icon}</span>}
                        <h1 className="text-4xl md:text-5xl font-bold gradient-text leading-tight">{title}</h1>
                    </div>

                    <div className="flex flex-wrap gap-4 mb-6">
                        {url && (
                            <a href={url} target="_blank" rel="noopener noreferrer"
                                className="px-4 py-2 bg-primary hover:bg-primary/80 transition-colors rounded-md text-white font-semibold text-sm flex items-center gap-2">
                                Visit Link <ExternalLink size={16} />
                            </a>
                        )}
                        {repo && (
                            <a href={repo} target="_blank" rel="noopener noreferrer"
                                className="px-4 py-2 bg-white/10 hover:bg-white/20 transition-colors rounded-md text-white font-semibold text-sm flex items-center gap-2 border border-white/10">
                                Repository <Github size={16} />
                            </a>
                        )}
                    </div>

                    <div className="flex flex-wrap gap-2 mb-6">
                        {tags.map((tag: string) => (
                            <span key={tag} className="px-3 py-1 bg-white/5 border border-white/10 rounded-full text-sm font-mono text-secondary">
                                {tag}
                            </span>
                        ))}
                    </div>

                    {summary && (
                        <p className="text-xl text-gray-300 leading-relaxed">
                            {summary}
                        </p>
                    )}
                </header>

                <div
                    className="markdown-content"
                    dangerouslySetInnerHTML={{ __html: contentHtml }}
                />
            </div>
        </article>
    );
}
