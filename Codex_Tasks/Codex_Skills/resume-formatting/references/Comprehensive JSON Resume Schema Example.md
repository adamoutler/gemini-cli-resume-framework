# **The JSON Resume Standard: A Comprehensive Architectural Analysis and Implementation Guide**

## **1\. Introduction: The Semantics of Professional Identity**

The digitization of human capital data has historically been plagued by a fundamental disconnect between presentation and structure. For decades, the curriculum vitae (CV) or resume has existed primarily as a layout-oriented document—typically a Microsoft Word file or Adobe PDF—designed for human visual consumption. While aesthetically flexible, these formats are opaque to machine interpretation. The rise of Applicant Tracking Systems (ATS), professional networking platforms, and AI-driven recruitment tools has created an urgent imperative for a standardized, machine-readable format that decouples the *content* of a professional history from its *presentation*.

The **JSON Resume** standard (v1.0.0) addresses this interoperability crisis by defining a strict schema for representing resume data in JavaScript Object Notation (JSON). This open-source initiative transforms the resume from a static document into a dynamic data object, enabling portability, version control, and seamless integration across the HR technology stack.1 By adhering to a schema-first approach, the standard ensures that a candidate’s data—ranging from contact details and employment history to granular skill taxonomies and project artifacts—can be parsed deterministically by any compliant system, be it a job board, a portfolio generator, or an analytics engine.3

This report provides an exhaustive technical analysis of the JSON Resume schema. It dissects every field, data type, and validation constraint defined in the specification, exploring the implications of these design choices for developers, recruiters, and candidates. Furthermore, it examines the broader ecosystem of tools—CLIs, themes, and validation utilities—that operationalize the schema. The analysis culminates in a definitive "Kitchen Sink" reference implementation: a monolithic JSON object that populates every possible field in the standard, serving as a master template for maximum data utilization.5

### **1.1 The Evolution of Resume Data Standards**

Before the advent of JSON Resume, attempts to standardize professional data relied on heavy, verbose formats like HR-XML or the European Union's Europass XML schema.6 While functional, these XML-based standards suffered from complexity, making them difficult for individual developers to adopt for personal websites or lightweight tools. JSON (JavaScript Object Notation) emerged as the *lingua franca* of the modern web, offering a lightweight, human-readable, and easily parsable alternative.

The JSON Resume initiative capitalizes on this by offering a schema that is:

1. **Machine-Readable:** Allowing ATS to ingest data with 100% accuracy, eliminating the parsing errors common with PDF scraping.2  
2. **Human-Friendly:** The JSON structure is intuitive enough that a user can edit their resume in a simple text editor without specialized software.5  
3. **Tool-Agnostic:** The separation of concerns means the same resume.json file can generate a PDF, a React-based website, or a terminal-based view without data duplication.1

### **1.2 The Schema Governance Model**

The schema is maintained by an open-source community and governed by Semantic Versioning (SemVer) principles. The current stable release, v1.0.0, represents a mature specification that balances rigidity (to ensure interoperability) with flexibility (to accommodate diverse career paths).6 Changes to the schema are managed through a transparent proposal process on GitHub, ensuring that new fields or deprecated properties are vetted for backward compatibility and utility.

Unlike proprietary formats controlled by closed platforms (e.g., LinkedIn's internal data model), JSON Resume prevents vendor lock-in. A user owns their data in a plain text format and can migrate between visualization tools or hosting platforms at will.1 This "sovereign identity" aspect is a core philosophical pillar of the project.

## ---

**2\. Technical Foundations: The JSON Schema Specification**

The structural integrity of a JSON Resume file is enforced by **JSON Schema**, a vocabulary that allows for the annotation and validation of JSON documents.8 The JSON Resume project utilizes standard JSON Schema definitions (compatible with Draft-04 through Draft-07) to define the allowable data types, required formats, and nesting rules for the resume object.9

### **2.1 Primitive Data Types and Constraints**

The schema relies on a specific set of primitive types to ensure consistency. Understanding these primitives is essential for constructing a valid "kitchen sink" example, as data type violations are the most common cause of validation failure.5

| Data Type | Usage Context | Schema Constraint | Example |
| :---- | :---- | :---- | :---- |
| **String** | General text | UTF-8 encoded text. No explicit length limit, but practical limits apply for rendering. | "Software Engineer" |
| **String (URL)** | Web links | Must be a valid URI string. Protocol (https://) is recommended. | "https://github.com" |
| **String (Email)** | Contact | Must follow standard email format (RFC 5322). | "user@example.com" |
| **String (ISO 8601\)** | Dates | Must follow YYYY-MM-DD, YYYY-MM, or YYYY. | "2023-06-15" |
| **Boolean** | Flags | true or false. Primarily used in meta configuration. | true |
| **Array** | Lists | Ordered collections of objects or strings. Preserves chronology. | \[...\] |
| **Object** | Grouping | Key-value pairs for structured entities. | { "address": "..." } |

### **2.2 The Criticality of Date Formatting**

One of the most robust features of the JSON Resume schema is its strict adherence to ISO 8601 date formats. In unstructured resumes, dates appear in chaotic variations ("Jan '20", "01/2020", "2020", "Winter 2020"), making chronological sorting impossible for machines.

The schema mandates that all date fields (e.g., startDate, endDate, date, releaseDate) utilize the standard ISO format.5 This standardization allows consuming applications to:

1. **Calculate Duration:** Automatically compute "Years of Experience" by subtracting start dates from end dates.  
2. **Detect Gaps:** Algorithmic identification of employment gaps becomes trivial and accurate.  
3. **Sort Chronologically:** Renderers can reliably order history regardless of the input order (though the convention is reverse-chronological).

Handling Current Roles:  
To indicate an ongoing position, the schema convention is to leave the endDate field as an empty string "" or omit it entirely. However, explicit inclusion of "" is the preferred "kitchen sink" approach to demonstrate that the field was considered and intentionally left open, triggering logic in themes to display "Present" or "Current".5

### **2.3 Semantic Separation of Concerns**

The schema enforces a separation between *what* the candidate did (responsibilities) and *what* they achieved (highlights). Most sections (Work, Volunteer, Projects) contain both a summary field (a string for narrative description) and a highlights field (an array of strings for bullet points).

This distinction is crucial for advanced rendering. A theme might display the summary in a standard paragraph font while rendering highlights as a bulleted list with distinct iconography. In an ATS context, highlights are often heavily weighted for keyword extraction as they typically contain specific metrics and technologies.2

## ---

**3\. The basics Object: Identity, Location, and Digital Presence**

The basics object is the root node for personal information. Unlike other top-level properties which are arrays (implying multiple entries), basics is a singular object, reflecting the singular identity of the candidate.5 This section is the most strictly validated by themes, as a resume without a name or contact method is functionally useless.

### **3.1 Identity and Branding Fields**

The fields within basics establish the professional brand of the individual.

* **name** (String): The full legal or professional name. While seemingly simple, this field serves as the document title in most parsers.  
* **label** (String): A professional headline (e.g., "Full Stack Systems Architect"). This is distinct from a job title; it describes the *person*, not their current role. It sets the context for the entire document.5  
* **image** (String, URL): A link to a hosted photograph.  
  * *Implementation Note:* In previous iterations, a picture field was discussed, but image is the standard in v1.0.0. The URL must be publicly accessible for the image to render in web views or PDF generators. This field is often omitted in US-centric resumes due to anti-discrimination norms but is standard in many European and Asian markets.2  
* **summary** (String): A professional biography. This is typically a 2-4 sentence paragraph. Markdown formatting (bold, italics) is often supported by themes here, though not strictly defined in the schema.2  
* **url** (String, URL): The candidate's primary web presence (e.g., portfolio, blog).  
  * *Deprecation Warning:* Older JSON files might use website. This has been standardized to url to match the naming convention used in other objects (like work or projects).5

### **3.2 Contact Information**

* **email** (String, Email): The primary communication channel. Validation logic often checks for the presence of an @ symbol and a domain.  
* **phone** (String): The contact number. While the schema accepts any string, utilizing the E.164 international standard (e.g., \+14155550123) is the "kitchen sink" best practice to ensure click-to-dial functionality works across borders.5

### **3.3 The location Object Structure**

Geospatial data is critical for "radius search" in recruitment platforms. The JSON Resume schema breaks location down into granular fields rather than a single string, enabling high-precision filtering.5

* **address** (String): Street address. Newline characters (\\n) are used to represent multi-line addresses (e.g., apartment numbers).  
* **postalCode** (String): Zip or postal code.  
* **city** (String): Municipality.  
* **countryCode** (String): The ISO 3166-1 alpha-2 code (e.g., US, GB, DE, FR).  
  * *Insight:* Using the 2-letter code is vital. An ATS looking for "United States" might miss "USA" or "America," but "US" is the globally recognized standard for data exchange.5  
* **region** (String): State, province, or prefecture (e.g., "California", "New South Wales").

### **3.4 The profiles Array: The Social Graph**

Modern professionals exist across a distributed network of platforms. The profiles array captures this graph, linking the resume to GitHub, LinkedIn, Behance, StackOverflow, and Twitter.5

* **network** (String): The platform name.  
  * *Rendering Logic:* Themes often map this string to icon font libraries (like FontAwesome). Therefore, the value should be the canonical name (e.g., "LinkedIn" or "Twitter") to ensure the correct icon appears. Using "My LinkedIn" might break the icon mapping.13  
* **username** (String): The handle on the platform.  
* **url** (String, URL): The direct hyperlink to the profile.

**Example Fragment:**

JSON

"profiles": \[  
  {  
    "network": "GitHub",  
    "username": "coder123",  
    "url": "https://github.com/coder123"  
  }  
\]

## ---

**4\. Professional Trajectory: The work and volunteer Arrays**

The core of any resume is the employment history. In JSON Resume, this is handled by the work array. A parallel structure exists for volunteer work, recognizing that unpaid experience often utilizes the same data points (organization, position, dates) as paid employment.5

### **4.1 The work Schema**

Each object in the work array represents a distinct role.

* **name** (String): The legal name of the employer.  
* **location** (String): The physical location of the office.  
  * *Note:* While basics has a structured location object, work uses a simple string. This is a deliberate design choice, as the semantic precision of an employer's address is generally less critical than the candidate's residence.5  
* **description** (String): A brief description of the company itself (e.g., "A Fortune 500 Fintech Company"). This provides context for the scale of the role.  
* **position** (String): The job title.  
* **url** (String, URL): The company website.  
  * *Consistency:* Like basics, this replaces legacy website fields.12  
* **startDate** (String, ISO 8601): Employment start.  
* **endDate** (String, ISO 8601): Employment end.  
* **summary** (String): A narrative overview of responsibilities.  
* **highlights** (Array): Specific achievements, typically rendered as bullet points.

Schema Insight: The "Highlights" vs. "Summary" Dichotomy  
The separation of these two fields allows for dual-mode reading. A human reader might scan the summary for context ("Managed a team of 5") and the highlights for impact ("Increased revenue by 20%"). An AI parser creates different weights for these fields; highlights are often treated as higher-signal data for skill extraction.2

### **4.2 The volunteer Schema**

The volunteer section is structurally identical to work but uses organization instead of name to identify the entity.5

* **organization** (String): The non-profit or group name.  
* **position** (String): The role (e.g., "Mentor", "Board Member").  
* **url** (String, URL): Website.  
* **startDate** / **endDate** (ISO 8601).  
* **summary** / **highlights**.

This separation ensures that unpaid work is not confused with employment history during automated background checks or years-of-experience calculations.16

## ---

**5\. Academic and Credential Verification: education, certificates, and awards**

Validating qualifications is a primary function of the background check process. The schema provides three distinct arrays to handle formal education, industry certifications, and accolades.

### **5.1 The education Array**

This section handles degrees and formal schooling.5

* **institution** (String): The university or school name.  
* **url** (String, URL): Website of the institution.  
* **area** (String): Major or field of study (e.g., "Computer Science").  
* **studyType** (String): The degree type (e.g., "Bachelor", "Master", "PhD").  
  * *Data Normalization:* Consistent use of terms (e.g., always "BS" vs "Bachelor of Science") assists parsers, though the schema does not enforce an enum here.5  
* **startDate** / **endDate** (ISO 8601): Enrollment period.  
* **score** (String): GPA or classification.  
  * *Flexibility:* Because grading systems vary globally (4.0 scale in US, 1st/2nd in UK, 1-6 in Germany), this is a free-text string rather than a number. Best practice is to include the scale (e.g., "3.8/4.0").5  
* **courses** (Array): A list of relevant coursework. This is particularly valuable for junior candidates who lack work experience but need to demonstrate relevant knowledge.5

### **5.2 The certificates Array**

As alternative education grows (bootcamps, MOOCs, vendor certifications), this array has become critical.5

* **name** (String): Certification title (e.g., "AWS Certified Solutions Architect").  
* **date** (String, ISO 8601): Date of issue.  
* **issuer** (String): The certifying body (e.g., "Amazon", "Cisco").  
* **url** (String, URL): A verification link. This is a crucial "trust" field, allowing a recruiter to instantly validate the claim against the issuer's database.

### **5.3 The awards Array**

Distinct from certifications, awards represent recognition of excellence.5

* **title** (String): Name of the award.  
* **date** (String, ISO 8601): Date received.  
* **awarder** (String): The organization granting the award.  
* **summary** (String): Context on why the award was given (e.g., "Selected from 500 nominees").

## ---

**6\. Competency Modeling: skills, languages, and interests**

While work history implies capability, the skills section makes it explicit. This data is the primary fuel for "keyword matching" algorithms used by ATS to filter candidates.2

### **6.1 The skills Taxonomy**

The schema encourages a hierarchical organization of skills rather than a flat list.5

* **name** (String): The category or domain (e.g., "Web Development", "DevOps").  
* **level** (String): Proficiency indicator.  
  * *Note:* While not an enforced enum, common values include "Beginner", "Intermediate", "Advanced", and "Master".14  
* **keywords** (Array): Specific technologies or tools (e.g., "React", "Docker", "Python").  
  * *SEO/ATS Strategy:* This is where the specific keywords from a Job Description (JD) should be matched. If a JD asks for "AWS," it should appear in this array.19

Schema vs. Usage:  
A common mistake is putting specific tools in name.

* *Incorrect:* { "name": "Java", "level": "Good" }  
* *Correct:* { "name": "Backend Development", "level": "Advanced", "keywords": }

### **6.2 The languages Array**

In an increasingly globalized workforce, language proficiency is a key differentiator.5

* **language** (String): The language name (e.g., "French").  
* **fluency** (String): Proficiency level.  
  * *Standard Levels:* The documentation suggests specific terms to ensure clarity: "Native", "Fluent", "Professional Working Proficiency", "Limited Working Proficiency", "Elementary", "Beginner". Adhering to these standard terms allows for better filtering (e.g., "Show candidates with Fluent Spanish").5

### **6.3 The interests Array**

This section provides "cultural fit" signals.5

* **name** (String): Interest category (e.g., "Music").  
* **keywords** (Array): Specifics (e.g., "Piano", "Jazz", "Composition").

## ---

**7\. Artifacts and Outputs: projects and publications**

For creators, developers, and researchers, the output of their work is as important as their employment history.

### **7.1 The projects Array**

This section captures side projects, open-source contributions, or specific major initiatives within a job.5

* **name** (String): Project title.  
* **description** (String): Overview.  
* **highlights** (Array): Achievements.  
* **keywords** (Array): Tech stack used.  
* **startDate** / **endDate** (ISO 8601).  
* **url** (String, URL): Link to the project (e.g., GitHub repo, live app).  
* **roles** (Array): Specific contributions (e.g., "Team Lead", "Designer").  
* **entity** (String): If the project was affiliated with a company or organization, it is listed here.  
* **type** (String): The category (e.g., "Application", "Conference", "Volunteer").

### **7.2 The publications Array**

Crucial for academic and research roles.5

* **name** (String): Title of the paper/book.  
* **publisher** (String): Journal or publisher name.  
* **releaseDate** (String, ISO 8601).  
* **url** (String, URL): DOI or link to text.  
* **summary** (String): Abstract.

## ---

**8\. Meta-Governance and Validation**

The meta object is unique; it contains data *about* the resume file, not the person.5

* **canonical** (String, URL): The source of truth URL. This is vital for version control. If a resume is downloaded and shared, this field points back to the live, up-to-date version.  
* **version** (String): A version string (e.g., "v1.0.1") for the user's personal tracking.  
* **lastModified** (String, ISO 8601): Timestamp of the last edit.  
* **skipValidation** (Boolean): A critical implementation flag.  
  * *Usage:* The official schema is strict. If a developer adds a custom field (e.g., projects.screenshots), the standard validator will throw an error. Setting skipValidation: true allows the JSON to pass through tooling despite these "illegal" fields. This is useful for custom themes that support extra data, but it breaks strict interoperability.5

### **8.1 References**

The references array is a simple list.5

* **name** (String): Referee name.  
* **reference** (String): The reference text. Note that many modern resumes omit this section ("References available upon request"), but the schema supports the full text if required.

## ---

**9\. Ecosystem Integration: Themes, CLI, and ATS**

The power of JSON Resume lies in its ecosystem. The resume.json file is rarely the final product; it is the *source* from which products are generated.

### **9.1 The Resume CLI**

The resume-cli tool is the standard interface for interacting with the schema.1

* **Validation:** resume validate resume.json runs the file against the official JSON Schema definitions, checking for type errors (e.g., putting a string in an array field) or format errors (invalid dates).  
* **Export:** resume export resume.pdf \--theme elegant compiles the JSON against a specific theme template (written in Handlebars, React, or Vue) to produce a styled document.  
* **Serving:** resume serve spins up a local web server with hot-reloading, allowing the user to edit the JSON and see changes instantly.20

### **9.2 ATS Integration Strategies**

For an ATS to digest a resume, it needs structure. "Modern CV" approaches embed the JSON data directly into the HTML version of the resume using a \<script\> tag:

HTML

\<script id\="cv-data-json" type\="application/json"\>  
  { "basics": {... } }  
\</script\>

When a recruiter views the HTML, they see the styled resume. When the ATS bot crawls the file, it locates this script tag, parses the JSON, and populates the database fields (Name, Email, Skills, History) with zero error rate. This "Dual Master" approach serves both human and machine audiences simultaneously.2

## ---

**10\. The "Kitchen Sink" Reference Implementation**

The following is a complete, syntactically valid JSON Resume object. It populates **every single field** defined in the v1.0.0 specification with data. It utilizes a fictional persona, "Maximillian Sterling," a highly qualified technology executive, to justify the breadth of data included.

This example serves as the ultimate test case for themes and parsers. If a system can process this file without error, it is fully compliant with the standard.

### **10.1 The JSON Object**

JSON

{  
  "$schema": "https://raw.githubusercontent.com/jsonresume/resume-schema/v1.0.0/schema.json",  
  "basics": {  
    "name": "Maximillian Sterling",  
    "label": "Distinguished Systems Architect & Polymath",  
    "image": "https://maximillian-sterling.com/profile-hd.jpg",  
    "email": "max@maximillian-sterling.com",  
    "phone": "+1 (415) 555-0199",  
    "url": "https://maximillian-sterling.com",  
    "summary": "A visionary architect with over 15 years of experience in distributed systems, artificial intelligence, and sustainable computing. Proven track record of leading global teams to deliver mission-critical infrastructure. Passionate about open standards and digital sovereignty.",  
    "location": {  
      "address": "42 Future Boulevard, Suite 1900",  
      "postalCode": "94105",  
      "city": "San Francisco",  
      "countryCode": "US",  
      "region": "California"  
    },  
    "profiles":  
  },  
  "work":  
    },  
    {  
      "name": "Nebula Startups Inc.",  
      "location": "Berlin, Germany",  
      "description": "An incubator and accelerator for high-growth SaaS platforms in the EMEA region.",  
      "position": "VP of Engineering",  
      "url": "https://nebula-startups.io",  
      "startDate": "2015-06-01",  
      "endDate": "2019-02-28",  
      "summary": "Led engineering teams across three portfolio companies, establishing best practices in CI/CD, microservices architecture, and remote team culture.",  
      "highlights":  
    },  
    {  
      "name": "BitStream Systems",  
      "location": "Remote",  
      "description": "A boutique consultancy focused on high-frequency trading algorithms.",  
      "position": "Senior Backend Engineer",  
      "url": "https://bitstream-sys.com",  
      "startDate": "2013-01-15",  
      "endDate": "2015-05-30",  
      "summary": "Designed low-latency execution engines for equities trading.",  
      "highlights":  
    }  
  \],  
  "volunteer":  
    },  
    {  
      "organization": "The Linux Foundation",  
      "position": "Contributor",  
      "url": "https://linuxfoundation.org",  
      "startDate": "2012-01-01",  
      "endDate": "2014-12-31",  
      "summary": "Contributed to kernel networking subsystems.",  
      "highlights":  
    }  
  \],  
  "education":  
    },  
    {  
      "institution": "Stanford University",  
      "url": "https://stanford.edu",  
      "area": "Electrical Engineering",  
      "studyType": "Bachelor of Science",  
      "startDate": "2006-09-01",  
      "endDate": "2010-06-15",  
      "score": "3.9/4.0",  
      "courses":  
    }  
  \],  
  "awards":,  
  "certificates":,  
  "publications":,  
  "skills":  
    },  
    {  
      "name": "Programming Languages",  
      "level": "Expert",  
      "keywords":  
    },  
    {  
      "name": "Data Systems",  
      "level": "Advanced",  
      "keywords":  
    }  
  \],  
  "languages":,  
  "interests": \[  
    {  
      "name": "High-Altitude Alpinism",  
      "keywords": \[  
        "Mountaineering",  
        "Ice Climbing",  
        "Acclimatization Physiology"  
      \]  
    },  
    {  
      "name": "Analog Synthesizers",  
      "keywords":  
    },  
    {  
      "name": "Chess",  
      "keywords":  
    }  
  \],  
  "references":,  
  "projects":,  
      "keywords":,  
      "startDate": "2017-01-01",  
      "endDate": "",  
      "url": "https://github.com/maxsterling/rust-net-lib",  
      "roles": \[  
        "Maintainer",  
        "Lead Architect"  
      \],  
      "entity": "Open Source Community",  
      "type": "Library"  
    },  
    {  
      "name": "SmartGrid AI",  
      "description": "An AI-powered grid balancing system for renewable energy providers, optimizing storage and distribution.",  
      "highlights":,  
      "keywords":,  
      "startDate": "2016-05-01",  
      "endDate": "2017-12-30",  
      "url": "https://smartgrid-ai.io",  
      "roles":,  
      "entity": "Self-Initiated",  
      "type": "Application"  
    }  
  \],  
  "meta": {  
    "canonical": "https://raw.githubusercontent.com/maxsterling/resume/master/resume.json",  
    "version": "v3.2.1",  
    "lastModified": "2024-01-15T10:30:00Z",  
    "skipValidation": false  
  }  
}

### **10.2 Implementation Analysis of the Example**

This "Kitchen Sink" example demonstrates several advanced capabilities:

1. **Concurrent Roles:** The candidate has an open-ended work role ("Chief Technology Officer") and an open-ended volunteer role ("Code for Humanity"), demonstrating how the schema handles parallel timelines.  
2. **Rich Metrics:** The highlights fields are populated with quantifiable data ("$500M", "40%", "10M connections"). This is critical for ATS scoring.  
3. **Complex Nesting:** The projects array includes keywords, roles, and entity, showcasing the depth of metadata available for portfolio items.  
4. **Global Data:** The use of international phone formats and diverse locations (Berlin, San Francisco) tests the parser's internationalization (i18n) capabilities.

## **11\. Conclusion**

The JSON Resume v1.0.0 standard represents a critical infrastructure layer for the future of work. By providing a strict, schema-backed definition of professional history, it enables a new generation of tools that treat careers as data, not documents. The "Kitchen Sink" example provided herein illustrates the standard's capacity to model the complexity of modern careers—spanning employment, open-source work, continuous learning, and global mobility—without losing semantic precision. For developers and systems architects, strict adherence to this schema ensures that the data remains portable, verifiable, and valuable across the entire HR technology ecosystem.

#### **Works cited**

1. JSON Resume Documentation, accessed December 15, 2025, [https://docs.jsonresume.org/](https://docs.jsonresume.org/)  
2. Modern CV Technology: JSON Resume embedded in HTML \- Paul Hammant's blog, accessed December 15, 2025, [https://paulhammant.com/2025/10/12/modern-cv-tech-json-resume-schema/](https://paulhammant.com/2025/10/12/modern-cv-tech-json-resume-schema/)  
3. JSON Resume: Standardized CV Format for Developers and Automation \- Angelo Lima, accessed December 15, 2025, [https://angelo-lima.fr/en/json-resume-standardized-cv-format-developers-automation/](https://angelo-lima.fr/en/json-resume-standardized-cv-format-developers-automation/)  
4. JSON Resume, accessed December 15, 2025, [https://jsonresume.org/](https://jsonresume.org/)  
5. Schema & Structure \- JSON Resume, accessed December 15, 2025, [https://docs.jsonresume.org/schema](https://docs.jsonresume.org/schema)  
6. jsonresume/resume-schema: JSON-Schema is used here to define and validate our proposed resume json \- GitHub, accessed December 15, 2025, [https://github.com/jsonresume/resume-schema](https://github.com/jsonresume/resume-schema)  
7. Releases · jsonresume/resume-schema \- GitHub, accessed December 15, 2025, [https://github.com/jsonresume/resume-schema/releases](https://github.com/jsonresume/resume-schema/releases)  
8. Specification \[\#section\] \- JSON Schema, accessed December 15, 2025, [https://json-schema.org/specification](https://json-schema.org/specification)  
9. resume-schema/job-schema.json at master · jsonresume/resume-schema \- GitHub, accessed December 15, 2025, [https://github.com/jsonresume/resume-schema/blob/master/job-schema.json](https://github.com/jsonresume/resume-schema/blob/master/job-schema.json)  
10. resume-schema/schema.json at master · jsonresume/resume-schema \- GitHub, accessed December 15, 2025, [https://github.com/jsonresume/resume-schema/blob/master/schema.json](https://github.com/jsonresume/resume-schema/blob/master/schema.json)  
11. I Built a Modern React Theme for JSON Resume \- DEV Community, accessed December 15, 2025, [https://dev.to/phoinixi/i-built-a-modern-react-theme-for-json-resume-d4h](https://dev.to/phoinixi/i-built-a-modern-react-theme-for-json-resume-d4h)  
12. CLI Tools \- JSON Resume Documentation, accessed December 15, 2025, [https://docs.jsonresume.org/cli](https://docs.jsonresume.org/cli)  
13. jcjones/jsonresume-theme-bootstrap-icons \- GitHub, accessed December 15, 2025, [https://github.com/jcjones/jsonresume-theme-bootstrap-icons](https://github.com/jcjones/jsonresume-theme-bootstrap-icons)  
14. Schema \- JSON Resume, accessed December 15, 2025, [https://jsonresume.org/schema](https://jsonresume.org/schema)  
15. Job Description Schema \- JSON Resume, accessed December 15, 2025, [https://jsonresume.org/job-description-schema](https://jsonresume.org/job-description-schema)  
16. How to Build a Developer JSON Resume 2024 \- Brian Douglass, accessed December 15, 2025, [https://bhdouglass.com/blog/how-to-build-a-developer-json-resume/](https://bhdouglass.com/blog/how-to-build-a-developer-json-resume/)  
17. Json On Resume: How To List Json Schema, Data Validation, Api Defin... \- VisualCV, accessed December 15, 2025, [https://www.visualcv.com/json-on-resume/](https://www.visualcv.com/json-on-resume/)  
18. keywords \- JSON Schema, accessed December 15, 2025, [https://json-schema.org/understanding-json-schema/keywords](https://json-schema.org/understanding-json-schema/keywords)  
19. Top Json Skills On Resume In 2025 \- VisualCV, accessed December 15, 2025, [https://www.visualcv.com/resume-skills/json/](https://www.visualcv.com/resume-skills/json/)  
20. JSON Resume \- Brian Douglass, accessed December 15, 2025, [https://bhdouglass.com/blog/json-resume/](https://bhdouglass.com/blog/json-resume/)