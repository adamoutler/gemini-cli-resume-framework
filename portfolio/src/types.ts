export interface Profile {
    network: string;
    username: string;
    url: string;
}

export interface Basics {
    name: string;
    label: string;
    image: string;
    email: string;
    phone: string;
    url: string;
    summary: string;
    location: {
        address: string;
        postalCode: string;
        city: string;
        countryCode: string;
        region: string;
    };
    profiles: Profile[];
}

export interface Work {
    name: string;
    company: string;
    position: string;
    startDate: string;
    endDate: string;
    summary: string;
    highlights: string[];
}

export interface Skill {
    name: string;
    level: string;
    keywords: string[];
}

export interface Project {
    name: string;
    description: string;
    keywords: string[];
    url: string;
}

export interface Resume {
    basics: Basics;
    work: Work[];
    skills: Skill[];
    projects: Project[];
    education: Record<string, unknown>[];
}
