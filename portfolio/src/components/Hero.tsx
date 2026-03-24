import { Basics } from "@/types";
import { Github, Linkedin, Mail, Globe, GraduationCap } from "lucide-react";

export default function Hero({ basics }: { basics: Basics }) {
    return (
        <section className="min-h-[80vh] flex flex-col justify-center items-center text-center px-4 relative overflow-hidden">
            {/* Abstract Background Elements */}
            <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-primary-glow rounded-full filter blur-[100px] opacity-30 animate-pulse"></div>
            <div className="absolute bottom-1/4 right-1/4 w-64 h-64 bg-accent/30 rounded-full filter blur-[100px] opacity-30 delay-1000 animate-pulse"></div>

            <div className="relative z-10 animate-fade-in space-y-6 max-w-4xl">
                <div className="inline-block px-3 py-1 mb-4 text-xs font-semibold tracking-wider text-primary uppercase bg-primary/10 rounded-full border border-primary/20">
                    Available for New Challenges
                </div>

                <h1 className="text-6xl md:text-8xl font-bold tracking-tight">
                    <span className="block">{basics.name}</span>
                    <span className="gradient-text text-4xl md:text-6xl mt-2 block">{basics.label}</span>
                </h1>

                <p className="text-lg md:text-xl text-secondary max-w-2xl mx-auto leading-relaxed">
                    {basics.summary.split('.')[0]}.
                </p>

                <div className="flex gap-4 justify-center mt-8">
                    {basics.profiles.map((profile) => {
                        const Icon = profile.network.toLowerCase().includes('github') ? Github :
                            profile.network.toLowerCase().includes('linkedin') ? Linkedin : 
                            profile.network.toLowerCase().includes('orcid') ? GraduationCap : Globe;
                        return (
                            <a
                                key={profile.network}
                                href={profile.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="p-3 glass-panel hover:bg-white/10 transition-colors rounded-full"
                            >
                                <Icon size={24} />
                            </a>
                        )
                    })}
                    <a
                        href={`mailto:${basics.email}`}
                        className="p-3 glass-panel hover:bg-white/10 transition-colors rounded-full"
                    >
                        <Mail size={24} />
                    </a>
                </div>
            </div>
        </section>
    );
}
