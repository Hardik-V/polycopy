export const CDN = "https://fs.cdn.poly.app/assets/landingpage/ec628e3/public";

export const NUXT = "https://poly.app/_nuxt";

// Pre-search floating images (the "desk" before search)
export const PRE_SEARCH_IMGS = Array.from({ length: 14 }, (_, i) =>
  `${CDN}/images/desk/assets/pre-search/${i + 1}.webp`
);

// Urban fashion images
export const URBAN_IMGS = Array.from({ length: 17 }, (_, i) =>
  `${CDN}/images/desk/assets/urban/${i + 1}.webp`
);

// Upcycled images
export const UPCYCLED_IMGS = Array.from({ length: 20 }, (_, i) =>
  `${CDN}/images/desk/assets/upcycled/${i + 1}.webp`
);

// Fashion images
export const FASHION_IMGS = Array.from({ length: 22 }, (_, i) =>
  `${CDN}/images/desk/assets/fashion/${i + 1}.webp`
);

// Search grid results
export const SEARCH_GRID = [
  { img: `${CDN}/images/desk/assets/search-grid/jackets_upcycled.jpg.webp`, label: "jackets_upcycled.jpg" },
  { img: `${CDN}/images/desk/assets/search-grid/model_upcycling01.jpg.webp`, label: "model_upcycling01.jpg" },
  { img: `${CDN}/images/desk/assets/search-grid/nikes_upcycled.jpg.webp`, label: "nikes_upcycled.jpg" },
  { img: `${CDN}/images/desk/assets/search-grid/re-use_film.mp4.webp`, label: "re-use_film.mp4" },
  { img: `${CDN}/images/desk/assets/search-grid/upcycling_report.docx.webp`, label: "upcycling_report.docx" },
  { img: `${CDN}/images/desk/assets/search-grid/tees_spring_summer.jpg.webp`, label: "tees_spring_summer.jpg" },
  { img: `${CDN}/images/desk/assets/search-grid/upcycled_shoot04.jpg.webp`, label: "upcycled_shoot04.jpg", highlighted: true },
  { img: `${CDN}/images/desk/assets/search-grid/re-use_interview.mp4.webp`, label: "re-use_interview.mp4" },
  { img: `${CDN}/images/desk/assets/fashion/19.webp`, label: "Garments.pdf" },
  { img: `${CDN}/images/desk/assets/search-grid/upcycling_fashion.pdf.webp`, label: "upcycling_fashion.pdf" },
  { img: `${CDN}/images/desk/assets/generic/mp3.webp`, label: "wasteful excess interview.mp3" },
  { img: `${CDN}/images/desk/assets/fashion/21.webp`, label: "Streetwear Upcycling Zine.pdf" },
];

// Deep search results
export const SEARCH_RESULTS = [
  { img: `${CDN}/images/desk/assets/search-results/upcycle_shoot02.jpg.webp`, label: "upcycle_shoot02.jpg" },
  { img: `${CDN}/images/desk/assets/search-results/upcycle_shoot05.jpg.webp`, label: "upcycle_shoot05.jpg" },
  { img: `${CDN}/images/desk/assets/fashion/1.webp`, label: "upcycling-reconstruction.pdf" },
  { img: `${CDN}/images/desk/assets/search-results/upcycled_interview_part2.mp4.webp`, label: "upcycled_interview_part2.mp4" },
  { img: `${CDN}/images/desk/assets/search-results/upcycle_shoot12.jpg.webp`, label: "upcycle_shoot12.jpg" },
  { img: `${CDN}/images/desk/assets/pre-search/1.webp`, label: "clothing-rack.jpg" },
  { img: `${CDN}/images/desk/assets/search-results/upcycle_shoot15.jpg.webp`, label: "upcycle_shoot15.jpg" },
  { img: `${CDN}/images/desk/assets/search-results/used_garments.docx.webp`, label: "used_garments.docx" },
  { img: `${CDN}/images/desk/assets/fashion/11.webp`, label: "sunglasses.jpg" },
  { img: `${CDN}/images/desk/assets/generic/mp3.webp`, label: "wasteful excess interview.mp3" },
  { img: `${CDN}/images/desk/assets/search-results/upcycled_interview.mp4.webp`, label: "upcycled_interview.mp4" },
  { img: `${CDN}/images/desk/assets/fashion/20.webp`, label: "Upcycling-mag-mar-25.pdf" },
];

// Showcase videos
export const SHOWCASE_VIDEOS = [
  {
    id: "analyze",
    title: "Analyze large folders of",
    titleHighlight: "content.",
    video: `${CDN}/videos/showcase/analyze.mp4`,
    tags: ["Knowledge Bases", "Archives", "Datasets"],
  },
  {
    id: "generate",
    title: "Generate images from entire folders of",
    titleHighlight: "references.",
    video: `${CDN}/videos/showcase/generate.mp4`,
    tags: ["Branding", "Visual Exploration", "Concepting"],
  },
  {
    id: "create",
    title: "Create intelligent notes and",
    titleHighlight: "summaries.",
    video: `${CDN}/videos/showcase/create.mp4`,
    tags: ["Knowledge Capture", "Research", "Coursework"],
  },
  {
    id: "search",
    title: "Search by content similarity, color",
    titleHighlight: "and more.",
    video: `${CDN}/videos/showcase/search.mp4`,
    tags: ["Visual Search", "Media Browsing"],
  },
  {
    id: "read",
    title: "Read complex",
    titleHighlight: "documents and diagrams.",
    video: `${CDN}/videos/showcase/read.mp4`,
    tags: ["Unstructured Data", "Blueprints", "Technical Reports"],
  },
  {
    id: "organize",
    title: "Tag and organize files",
    titleHighlight: "automatically.",
    video: `${CDN}/videos/showcase/organize.mp4`,
    tags: ["File Management", "Workflow Automations"],
  },
];

// View modes
export const VIEW_MODES = [
  { label: "Feed", img: `${CDN}/images/view-modes/feed.webp` },
  { label: "Grid", img: `${CDN}/images/view-modes/grid.webp` },
  { label: "Icon", img: `${CDN}/images/view-modes/file.webp` },
  { label: "Tree", img: `${CDN}/images/view-modes/tree.webp` },
  { label: "Column", img: `${CDN}/images/view-modes/column.webp` },
  { label: "Gallery", img: `${CDN}/images/view-modes/gallery.webp` },
];

// Features grid
export const FEATURES = [
  { num: "01", title: "Desktop Sync", desc: "Access and sync Poly files in your local file system", img: `${CDN}/images/features/Desktop Sync.webp`, icon: `${NUXT}/01.C3wFy9aT.svg` },
  { num: "02", title: "Long Context", desc: "Read thousands of files in a single conversation, and hold multiple simultaneous conversations at once", img: `${CDN}/images/features/Long Context.webp`, icon: `${NUXT}/02.C0dNyOrZ.svg` },
  { num: "03", title: "Version History", desc: "Your entire file system has full version history for every file, letting you revert to previous versions right from the UI", img: `${CDN}/images/features/Version History.webp`, icon: `${NUXT}/03.DT4aPcuw.svg` },
  { num: "04", title: "Public Sharing", desc: "Share your files with the world with the click of a button, and let anyone browse, download, and even search your public folders", img: `${CDN}/images/features/Public Sharing.webp`, icon: `${NUXT}/04.BF0Zo2qs.svg` },
  { num: "05", title: "Flexible Viewing", desc: "Sort, group, filter, and attach whichever properties to your file view so that you get the perfect flow for your files", img: `${CDN}/images/features/Flexible Viewing.webp`, icon: `${NUXT}/05.CuLqwvE1.svg` },
  { num: "06", title: "Shared Drives", desc: "Collaborate on files with others, with separate permissions and real-time updates", img: `${CDN}/images/features/Shared Drives.webp`, icon: `${NUXT}/06.CEHdEaqO.svg` },
  { num: "07", title: "Hide from AI", desc: "With the click of a button, hide your files from search and AI to never have the agent accidentally read your private files", img: `${CDN}/images/features/Hide from AI.webp`, icon: `${NUXT}/07.hu-XXgDr.svg` },
  { num: "08", title: "Extensive File Properties", desc: "Attach rich metadata and properties to any file for powerful filtering and organization", img: `${CDN}/images/features/Extensive File Properties.webp`, icon: `${NUXT}/08.D_MsJ_-T.svg` },
  { num: "09", title: "Privacy and Security", desc: "Your files stay encrypted on your device, in transit, and in the cloud, protected by a privacy-first infrastructure", img: `${CDN}/images/features/Privacy and Security.webp`, icon: `${NUXT}/09.Ck5zIWeb.svg` },
  { num: "10", title: "Offline Support", desc: "Use both the web and desktop apps offline, with your file changes syncing to the cloud when you come back", img: `${CDN}/images/features/Offline Support.webp`, icon: `${NUXT}/10.D01kby7s.svg` },
  { num: "11", title: "Fluent UI", desc: "Press spacebar to peek any file. Interact with right click, drag, and selection gestures just like a native app", img: `${CDN}/images/features/Fluent UI.webp`, icon: `${NUXT}/11.CKnpQ4al.svg` },
  { num: "12", title: "Collaborative Conversations", desc: "(Coming soon) collaborate on conversations with others, letting them send messages and interact with the model with you in real time", img: `${CDN}/images/features/Collaborative Conversations.webp`, icon: `${NUXT}/12.fOWxpxHs.svg` },
];

// Animated drawings CDN base
export const DRAWINGS_CDN = `${CDN}/images/animated-drawings`;

// File types for the belt
export const FILE_TYPES = [
  "JPG", "MP4", "PDF", "PNG", "MOV", "DOCX", "MP3", "AI", "PSD", "SVG",
  "ZIP", "CSV", "XLSX", "RAW", "TIFF", "GIF", "WEBP", "HEIC", "AAC", "FLAC",
];

// Search pill suggestions
export const SEARCH_PILLS = [
  "UrbanUpcycledClothing",
  "shots of model in red",
  "brand guidelines",
  "page 4 of the pitch deck",
  "video of the warehouse",
];