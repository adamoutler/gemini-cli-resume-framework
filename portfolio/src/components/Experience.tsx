import { Work } from "@/types";

export default function Experience({ work }: { work: Work[] }) {
    return (
        <section className="py-20 relative">
            <div className="container mx-auto px-4">
                <h2 className="text-4xl font-bold mb-16 text-center">
                    <span className="gradient-text">Experience</span>
                </h2>

                <div className="relative space-y-12">
                    {/* Vertical line */}
                    <div className="absolute left-4 md:left-1/2 top-4 bottom-4 w-0.5 bg-gradient-to-b from-primary/50 via-purple-500/50 to-primary/0 md:-ml-[1px]"></div>

                    {work.map((job, index) => (
                        <div key={index} className={`relative flex flex-col md:flex-row gap-8 ${index % 2 === 0 ? 'md:flex-row-reverse' : ''}`}>

                            {/* Timeline Dot */}
                            <div className="absolute left-4 md:left-1/2 w-4 h-4 bg-primary rounded-full border-4 border-background transform -translate-x-1/2 mt-1.5 z-10 shadow-[0_0_10px_var(--primary)]"></div>

                            {/* Content */}
                            <div className="ml-12 md:ml-0 md:w-1/2">
                                <div className="glass-panel p-6 md:p-8 hover:border-primary/30 transition-all duration-300 group">
                                    <div className="flex flex-col md:flex-row justify-between mb-4 gap-2">
                                        <div>
                                            <h3 className="text-xl font-bold group-hover:text-primary transition-colors">{job.position}</h3>
                                            <p className="text-secondary font-medium">{job.company}</p>
                                        </div>
                                        <div className="text-sm font-mono text-secondary/80 bg-white/5 py-1 px-3 rounded-full h-fit w-fit whitespace-nowrap">
                                            {job.startDate} — {job.endDate || 'Present'}
                                        </div>
                                    </div>

                                    <p className="text-gray-300 mb-6 leading-relaxed">
                                        {job.summary}
                                    </p>

                                    <ul className="space-y-2">
                                        {job.highlights.map((highlight, i) => (
                                            <li key={i} className="flex gap-3 text-sm text-gray-400">
                                                <span className="text-primary mt-1.5">▹</span>
                                                <span>{highlight}</span>
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            </div>

                            {/* Empty side for layout balance */}
                            <div className="hidden md:block md:w-1/2"></div>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
}
