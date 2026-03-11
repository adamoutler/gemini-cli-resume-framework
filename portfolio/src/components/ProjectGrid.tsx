import Link from 'next/link';
import { ExternalLink, ArrowRight } from "lucide-react";

export interface DisplayProject {
    title: string;
    description: string;
    link?: string;      // External URL
    slug?: string;      // Internal Slug
    tags: string[];
}

export default function ProjectGrid({ projects }: { projects: DisplayProject[] }) {
    return (
        <section className="py-20 container mx-auto px-4">
            <h2 className="text-4xl font-bold mb-12 text-center">
                <span className="gradient-text">Featured Projects</span>
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                {projects.map((project, index) => (
                    <div key={index} className="glass-panel p-6 flex flex-col h-full group hover:-translate-y-2 transition-transform duration-300">
                        <div className="flex-1">
                            <h3 className="text-2xl font-bold mb-3 group-hover:text-primary transition-colors">
                                {project.title}
                            </h3>
                            <p className="text-gray-400 mb-6 line-clamp-3">
                                {project.description}
                            </p>

                            <div className="flex flex-wrap gap-2 mb-6">
                                {project.tags.slice(0, 4).map(tag => (
                                    <span key={tag} className="text-xs font-mono text-secondary bg-black/30 px-2 py-1 rounded">
                                        {tag}
                                    </span>
                                ))}
                            </div>
                        </div>

                        <div className="mt-auto pt-4 border-t border-white/5 flex gap-4">
                            {project.slug && (
                                <Link
                                    href={`/projects/${project.slug}`}
                                    className="flex items-center gap-2 text-sm font-semibold text-primary hover:text-primary/80 transition-colors"
                                >
                                    Read More <ArrowRight size={16} />
                                </Link>
                            )}
                            {project.link && (
                                <a
                                    href={project.link}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="flex items-center gap-2 text-sm font-semibold text-secondary hover:text-white transition-colors ml-auto"
                                >
                                    External <ExternalLink size={16} />
                                </a>
                            )}
                        </div>
                    </div>
                ))}
            </div>
        </section>
    );
}
