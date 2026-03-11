import fs from 'fs';
import path from 'path';
import matter from 'gray-matter';

// Content Root
const DATA_DIR = path.join(process.cwd(), '../cv-data');

export interface TreeNode {
    name: string;
    path: string; // URL path (e.g., "/folder/file")
    slug: string[]; // split path for Next.js catch-all
    type: 'folder' | 'file';
    children?: TreeNode[];
    frontmatter?: Record<string, unknown>;
    content?: string;
}

// Map for pretty folder names
const FOLDER_MAP: Record<string, string> = {
    'professional-experience': 'Professional Experience',
    'personal-projects': 'Personal Projects',
    'authored-articles': 'Articles',
    'business_logic': 'Business Logic',
    'general': 'General',
    'news-media-mentions': 'Media Mentions',
};

function formatName(name: string): string {
    if (FOLDER_MAP[name]) return FOLDER_MAP[name];
    // Fallback: capitalized words
    return name.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

// Helper to resolve the correct data directory
function getDataDir(): string | null {
    if (fs.existsSync(DATA_DIR)) return DATA_DIR;

    // Priority 2: Docker / Production (copied to ./data/cv-data)
    // We want the ROOT of the site to be the contents of cv-data, not the data folder itself.
    const dockerCvData = path.join(process.cwd(), 'data', 'cv-data');
    if (fs.existsSync(dockerCvData)) return dockerCvData;

    // Fallback: Just ./data (if structure changes)
    const localData = path.join(process.cwd(), 'data');
    if (fs.existsSync(localData)) return localData;

    return null;
}

export function getTree(): TreeNode[] {
    const targetDir = getDataDir();
    if (!targetDir) return [];

    const tree: TreeNode[] = [];
    build(targetDir, tree);
    return tree;
}

function build(currentPath: string, parentNode: TreeNode[], relativePathParts: string[] = []) {
    const items = fs.readdirSync(currentPath);

    // Filter Configuration
    const EXCLUDED_FOLDERS = ['Business_logic', 'general'];
    const EXCLUDED_FILE_PATTERN = /NORAG/i;

    // Sort: directories first, then files
    items.sort((a, b) => {
        const pathA = path.join(currentPath, a);
        const pathB = path.join(currentPath, b);
        const statA = fs.statSync(pathA);
        const statB = fs.statSync(pathB);

        if (statA.isDirectory() && !statB.isDirectory()) return -1;
        if (!statA.isDirectory() && statB.isDirectory()) return 1;
        return a.localeCompare(b);
    });

    for (const item of items) {
        if (item.startsWith('.')) continue; // Ignore dotfiles
        if (EXCLUDED_FOLDERS.includes(item)) continue; // Ignore specific folders
        if (EXCLUDED_FILE_PATTERN.test(item)) continue; // Ignore NORAG files

        const fullPath = path.join(currentPath, item);
        const stat = fs.statSync(fullPath);
        const newSlug = [...relativePathParts, item.replace('.md', '')];
        const urlPath = '/' + newSlug.join('/');

        if (stat.isDirectory()) {
            const node: TreeNode = {
                name: formatName(item),
                path: urlPath,
                slug: newSlug,
                type: 'folder',
                children: []
            };
            build(fullPath, node.children!, newSlug);
            if (node.children!.length > 0) { // Only add non-empty folders
                parentNode.push(node);
            }
        } else if (item.endsWith('.md')) {
            // Attempt read for title
            const fileContents = fs.readFileSync(fullPath, 'utf8');
            let name = item.replace('.md', '').replace(/-/g, ' ');
            let frontmatter = {};
            try {
                const parsed = matter(fileContents);
                frontmatter = parsed.data;
                if (parsed.data.title) name = parsed.data.title as string;
            } catch {
                // ignore
            }

            parentNode.push({
                name,
                path: urlPath,
                slug: newSlug,
                type: 'file',
                frontmatter
            });
        }
    }
}

export function getItemBySlug(slug: string[]): TreeNode | null {
    const tree = getTree();

    // Traverse tree to find the item
    let currentLevel = tree;
    let foundNode: TreeNode | null = null;

    for (let i = 0; i < slug.length; i++) {
        const part = slug[i];
        // Match either folder name (raw) or file slug
        const node = currentLevel.find(n => {
            // reconstruct slug part logic 
            // The API builds slug from filename, so last part matches
            return n.slug[n.slug.length - 1] === part;
        });

        if (!node) return null;

        if (i === slug.length - 1) {
            foundNode = node;
        } else {
            if (node.children) {
                currentLevel = node.children;
            } else {
                return null;
            }
        }
    }

    // If it's a file, we might want to attach content here if needed,
    // but we can also read it on demand to keep tree light.
    // For the page render, we definitely need content.
    if (foundNode && foundNode.type === 'file') {
        const targetDir = getDataDir();
        if (!targetDir) return foundNode; // Should not happen if tree exists

        // NOTE: Directories don't end in .md, files do.
        let filePath = path.join(targetDir, ...slug);
        if (!fs.existsSync(filePath)) {
            // Try adding .md
            filePath = filePath + '.md';
        }

        if (fs.existsSync(filePath) && fs.statSync(filePath).isFile()) {
            const fileContents = fs.readFileSync(filePath, 'utf8');
            // Strip Frontmatter
            const parsed = matter(fileContents);
            return {
                ...foundNode,
                content: parsed.content // Return content only
            };
        }
    }

    return foundNode;
}
