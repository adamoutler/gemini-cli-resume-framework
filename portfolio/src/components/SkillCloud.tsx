import { Skill } from "@/types";

export default function SkillCloud({ skills }: { skills: Skill[] }) {
    return (
        <section className="py-20 bg-black/20">
            <div className="container mx-auto px-4 text-center">
                <h2 className="text-4xl font-bold mb-12">
                    <span className="gradient-text">Skills & Technologies</span>
                </h2>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
                    {skills.map((skillGroup) => (
                        <div key={skillGroup.name} className="glass-panel p-6 text-left hover:bg-white/5 transition-colors">
                            <h3 className="text-xl font-semibold mb-2 text-primary">{skillGroup.name}</h3>
                            <p className="text-sm text-secondary mb-4 uppercase tracking-wider text-xs">{skillGroup.level}</p>
                            <div className="flex flex-wrap gap-2">
                                {skillGroup.keywords.map((keyword) => (
                                    <span
                                        key={keyword}
                                        className="px-3 py-1 bg-white/10 rounded-full text-sm hover:bg-white/20 transition-colors border border-white/5"
                                    >
                                        {keyword}
                                    </span>
                                ))}
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
}
