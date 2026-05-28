"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);

// ─── CDN base ────────────────────────────────────────────────────────────────
const CDN = "https://fs.cdn.poly.app/assets/landingpage/ec628e3/public";
const NUXT = "https://poly.app/_nuxt";

// ─── Data ─────────────────────────────────────────────────────────────────────
const FILE_TYPES = ["mp3","jpg","docx","mov","xlsx","flac","tiff","pptx","txt","html","url","py","pdf","psd","zip","webp","mkv","mp4","raw","heif"];

const SHOWCASE_SLIDES = [
  { sans: "Analyze large folders of ", serif: "content.", tags: ["Knowledge Bases","Archives","Datasets"], video: `${CDN}/videos/showcase/analyze.mp4` },
  { sans: "Generate images from entire folders of ", serif: "references.", tags: ["Branding","Visual Exploration","Concepting"], video: `${CDN}/videos/showcase/generate.mp4` },
  { sans: "Create intelligent notes and ", serif: "summaries.", tags: ["Knowledge Capture","Research","Coursework"], video: `${CDN}/videos/showcase/create.mp4` },
  { sans: "Search by content similarity, color ", serif: "and more.", tags: ["Visual Search","Media Browsing"], video: `${CDN}/videos/showcase/search.mp4` },
  { sans: "Read complex ", serif: "documents and diagrams.", tags: ["Unstructured Data","Blueprints","Technical Reports"], video: `${CDN}/videos/showcase/read.mp4` },
  { sans: "Tag and organize files ", serif: "automatically.", tags: ["File Management","Workflow Automations"], video: `${CDN}/videos/showcase/organize.mp4` },
];

const VIEW_MODES = [
  { label: "Feed",    img: `${CDN}/images/view-modes/feed.webp` },
  { label: "Grid",    img: `${CDN}/images/view-modes/grid.webp` },
  { label: "Icon",    img: `${CDN}/images/view-modes/file.webp` },
  { label: "Tree",    img: `${CDN}/images/view-modes/tree.webp` },
  { label: "Column",  img: `${CDN}/images/view-modes/column.webp` },
  { label: "Gallery", img: `${CDN}/images/view-modes/gallery.webp` },
];

const FEATURES = [
  { title: "Desktop Sync",             desc: "Access and sync Poly files in your local file system",                                                                                     img: `${CDN}/images/features/Desktop Sync.webp`,              icon: `${NUXT}/01.C3wFy9aT.svg` },
  { title: "Long Context",             desc: "Read thousands of files in a single conversation, and hold multiple simultaneous conversations at once",                                    img: `${CDN}/images/features/Long Context.webp`,              icon: `${NUXT}/02.C0dNyOrZ.svg` },
  { title: "Version History",          desc: "Your entire file system has full version history for every file, letting you revert to previous versions right from the UI",               img: `${CDN}/images/features/Version History.webp`,           icon: `${NUXT}/03.DT4aPcuw.svg` },
  { title: "Public Sharing",           desc: "Share your files with the world with the click of a button, and let anyone browse, download, and even search your public folders",         img: `${CDN}/images/features/Public Sharing.webp`,            icon: `${NUXT}/04.BF0Zo2qs.svg` },
  { title: "Flexible Viewing",         desc: "Sort, group, filter, and attach whichever properties to your file view so that you get the perfect flow for your files",                   img: `${CDN}/images/features/Flexible Viewing.webp`,          icon: `${NUXT}/05.CuLqwvE1.svg` },
  { title: "Shared Drives",            desc: "Collaborate on files with others, with separate permissions and real-time updates",                                                         img: `${CDN}/images/features/Shared Drives.webp`,             icon: `${NUXT}/06.CEHdEaqO.svg` },
  { title: "Hide from AI",             desc: "With the click of a button, hide your files from search and AI to never have the agent accidentally read your private files",              img: `${CDN}/images/features/Hide from AI.webp`,              icon: `${NUXT}/07.hu-XXgDr.svg` },
  { title: "Extensive File Properties",desc: "Rich metadata, EXIF data, and custom properties visible for every file in your library",                                                   img: `${CDN}/images/features/Extensive File Properties.webp`, icon: `${NUXT}/08.D_MsJ_-T.svg` },
  { title: "Privacy and Security",     desc: "Your files stay encrypted on your device, in transit, and in the cloud, protected by a privacy-first infrastructure",                     img: `${CDN}/images/features/Privacy and Security.webp`,      icon: `${NUXT}/09.Ck5zIWeb.svg` },
  { title: "Offline Support",          desc: "Use both the web and desktop apps offline, with your file changes syncing to the cloud when you come back",                                img: `${CDN}/images/features/Offline Support.webp`,           icon: `${NUXT}/10.D01kby7s.svg` },
  { title: "Fluent UI",                desc: "Press spacebar to peek any file. Interact with right click, drag, and selection gestures just like a native app",                         img: `${CDN}/images/features/Fluent UI.webp`,                 icon: `${NUXT}/11.CKnpQ4al.svg` },
  { title: "Collaborative Conversations",desc: "(Coming soon) collaborate on conversations with others, letting them send messages and interact with the model with you in real time",   img: `${CDN}/images/features/Collaborative Conversations.webp`,icon: `${NUXT}/12.fOWxpxHs.svg` },
];

const SEARCH_QUERIES = ["Urban Upcycled Clothing","Red abstract textures","Q4 financial reports","Profile photos from shoot","Product videos March"];

const PRE_SEARCH = Array.from({ length: 14 }, (_, i) => `${CDN}/images/desk/assets/pre-search/${i + 1}.webp`);
const URBAN      = Array.from({ length: 17 }, (_, i) => `${CDN}/images/desk/assets/urban/${i + 1}.webp`);
const UPCYCLED   = Array.from({ length: 20 }, (_, i) => `${CDN}/images/desk/assets/upcycled/${i + 1}.webp`);
const FASHION    = Array.from({ length: 22 }, (_, i) => `${CDN}/images/desk/assets/fashion/${i + 1}.webp`);

const SEARCH_GRID = [
  { img: `${CDN}/images/desk/assets/search-grid/jackets_upcycled.jpg.webp`,    name: "jackets_upcycled.jpg" },
  { img: `${CDN}/images/desk/assets/search-grid/model_upcycling01.jpg.webp`,   name: "model_upcycling01.jpg" },
  { img: `${CDN}/images/desk/assets/search-grid/nikes_upcycled.jpg.webp`,      name: "nikes_upcycled.jpg" },
  { img: `${CDN}/images/desk/assets/search-grid/re-use_film.mp4.webp`,         name: "re-use_film.mp4" },
  { img: `${CDN}/images/desk/assets/search-grid/upcycling_report.docx.webp`,   name: "upcycling_report.docx" },
  { img: `${CDN}/images/desk/assets/search-grid/tees_spring_summer.jpg.webp`,  name: "tees_spring_summer.jpg" },
  { img: `${CDN}/images/desk/assets/search-grid/upcycled_shoot04.jpg.webp`,    name: "upcycled_shoot04.jpg", active: true },
  { img: `${CDN}/images/desk/assets/search-grid/re-use_interview.mp4.webp`,    name: "re-use_interview.mp4" },
  { img: `${CDN}/images/desk/assets/fashion/19.webp`,                          name: "Garments.pdf" },
  { img: `${CDN}/images/desk/assets/search-grid/upcycling_fashion.pdf.webp`,   name: "upcycling_fashion.pdf" },
  { img: `${CDN}/images/desk/assets/generic/mp3.webp`,                         name: "wasteful excess interview.mp3" },
  { img: `${CDN}/images/desk/assets/fashion/21.webp`,                          name: "Streetwear Upcycling Zine.pdf" },
];

const SEARCH_RESULTS = [
  { img: `${CDN}/images/desk/assets/search-results/upcycle_shoot02.jpg.webp`,       name: "upcycle_shoot02.jpg" },
  { img: `${CDN}/images/desk/assets/search-results/upcycle_shoot05.jpg.webp`,       name: "upcycle_shoot05.jpg" },
  { img: `${CDN}/images/desk/assets/fashion/1.webp`,                                name: "upcycling-reconstruction.pdf" },
  { img: `${CDN}/images/desk/assets/search-results/upcycled_interview_part2.mp4.webp`, name: "upcycled_interview_part2.mp4", active: true },
  { img: `${CDN}/images/desk/assets/search-results/upcycle_shoot12.jpg.webp`,       name: "upcycle_shoot12.jpg" },
  { img: `${CDN}/images/desk/assets/pre-search/1.webp`,                             name: "clothing-rack.jpg" },
  { img: `${CDN}/images/desk/assets/search-results/upcycle_shoot15.jpg.webp`,       name: "upcycle_shoot15.jpg" },
  { img: `${CDN}/images/desk/assets/search-results/used_garments.docx.webp`,        name: "used_garments.docx" },
  { img: `${CDN}/images/desk/assets/fashion/11.webp`,                               name: "sunglasses.jpg" },
  { img: `${CDN}/images/desk/assets/generic/mp3.webp`,                              name: "wasteful excess interview.mp3" },
  { img: `${CDN}/images/desk/assets/search-results/upcycled_interview.mp4.webp`,    name: "upcycled_interview.mp4" },
  { img: `${CDN}/images/desk/assets/fashion/20.webp`,                               name: "Upcycling-mag-mar-25.pdf" },
];

// ─── Animated drawing ─────────────────────────────────────────────────────────
function AnimDrawing({ name, className = "", style = {} }: { name: string; className?: string; style?: React.CSSProperties }) {
  const base = `${CDN}/images/animated-drawings`;
  const wrapRef = useRef<HTMLDivElement>(null);
  const [active, setActive] = useState(false);

  useEffect(() => {
    if (!wrapRef.current) return;
    const obs = new IntersectionObserver(([e]) => { if (e.isIntersecting) setActive(true); }, { threshold: 0.5 });
    obs.observe(wrapRef.current);
    return () => obs.disconnect();
  }, []);

  return (
    <div ref={wrapRef} className={className} style={{ position: "relative", ...style }}>
      <img src={`${base}/${name} default.png`} alt="" style={{ position: "absolute", inset: 0, width: "100%", opacity: active ? 0 : 1, transition: "opacity 0.4s ease" }} />
      <img src={`${base}/${name} in.png`}      alt="" style={{ position: "absolute", inset: 0, width: "100%", opacity: active ? 1 : 0, transition: "opacity 0.4s ease" }} />
    </div>
  );
}

// ─── Poly Logo ────────────────────────────────────────────────────────────────
function PolyLogo({ style = {} }: { style?: React.CSSProperties }) {
  return (
    <svg width="138" height="47" viewBox="0 0 138 47" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ width: "8.625rem", height: "3rem", ...style }}>
      <path fill="#fff" d="M59.08 38.902V8.039h12.345c6.04 0 10.008 3.66 10.008 9.171 0 5.6-3.968 9.215-10.008 9.215h-7.187v12.477zm5.158-16.886h6.658c3.262 0 5.379-1.896 5.379-4.806 0-2.866-2.117-4.718-5.38-4.718h-6.657zm28.979 17.239c-6.658 0-11.463-4.806-11.463-11.508s4.805-11.419 11.463-11.419 11.463 4.718 11.463 11.42c0 6.745-4.806 11.507-11.463 11.507m0-4.145c3.88 0 6.57-2.998 6.57-7.363 0-4.276-2.69-7.274-6.57-7.274-3.836 0-6.57 2.954-6.57 7.274 0 4.365 2.734 7.363 6.57 7.363m20.809 4.145c-3.791 0-6.304-2.073-6.304-6.922V7.687h4.805v24.425c0 2.16.838 2.91 2.249 2.91a6.1 6.1 0 0 0 2.292-.44v4.1c-.661.308-1.895.573-3.042.573m6.618 7.671 3.483-8.333-8.686-21.912h5.203l5.996 15.74 5.952-15.74h5.07l-11.948 30.245z"/>
      <g clipPath="url(#plc)">
        <path fill="url(#plb)" d="m30.538 19.612 14.299 13.81L32.64.3z" opacity=".5"/>
        <path fill="url(#plc2)" d="M45 33.91 32.759 0l-2.156 19.58z"/>
        <path fill="url(#pld)" d="M24.148 29.576 45 33.91 30.603 19.58z"/>
        <path fill="url(#ple)" d="M30.603 19.58 32.759 0 21.71 17.838l8.892 1.741Z"/>
        <path fill="url(#plf)" d="M0 13.585 12.848 47l2.702-19.215z"/>
        <path fill="url(#plg)" d="M32.759 0 0 13.585l21.712 4.253z"/>
        <path fill="url(#plh)" d="M24.148 29.576 12.848 47 45 33.91z"/>
        <path fill="url(#pli)" d="M15.55 27.785 12.848 47l11.3-17.424-8.598-1.79Z"/>
        <path fill="url(#plj)" d="M21.712 17.838 0 13.585l15.55 14.2 8.598 1.79 6.455-9.996-8.892-1.74Z"/>
      </g>
      <defs>
        <linearGradient id="plc2" x1="30.603" x2="45" y1="16.953" y2="16.953" gradientUnits="userSpaceOnUse"><stop stopColor="#FFBA84"/><stop offset=".57" stopColor="#FC5C32"/><stop offset=".99" stopColor="#EE2017"/></linearGradient>
        <linearGradient id="pld" x1="40.868" x2="26.463" y1="38.069" y2="23.741" gradientUnits="userSpaceOnUse"><stop stopColor="#FFBA84"/><stop offset=".57" stopColor="#FC5C32"/><stop offset=".99" stopColor="#EE2017"/></linearGradient>
        <linearGradient id="ple" x1="27.233" x2="27.233" y1="19.579" y2="0" gradientUnits="userSpaceOnUse"><stop stopColor="#FFBA84"/><stop offset=".57" stopColor="#FC5C32"/><stop offset=".99" stopColor="#EE2017"/></linearGradient>
        <linearGradient id="plf" x1="0" x2="15.55" y1="30.293" y2="30.293" gradientUnits="userSpaceOnUse"><stop stopColor="#FFBA84"/><stop offset=".57" stopColor="#FC5C32"/><stop offset=".99" stopColor="#EE2017"/></linearGradient>
        <linearGradient id="plg" x1="16.377" x2="16.377" y1="17.838" y2="0" gradientUnits="userSpaceOnUse"><stop stopColor="#FFBA84"/><stop offset=".57" stopColor="#FC5C32"/><stop offset=".99" stopColor="#EE2017"/></linearGradient>
        <linearGradient id="plh" x1="16.125" x2="38.83" y1="50.294" y2="27.707" gradientUnits="userSpaceOnUse"><stop stopColor="#FFBA84"/><stop offset=".57" stopColor="#FC5C32"/><stop offset=".99" stopColor="#EE2017"/></linearGradient>
        <linearGradient id="pli" x1="18.496" x2="18.496" y1="47" y2="27.785" gradientUnits="userSpaceOnUse"><stop stopColor="#FFBA84"/><stop offset=".57" stopColor="#FC5C32"/><stop offset=".99" stopColor="#EE2017"/></linearGradient>
        <linearGradient id="plj" x1="15.302" x2="15.302" y1="29.576" y2="13.589" gradientUnits="userSpaceOnUse"><stop stopColor="#FFBA84"/><stop offset=".57" stopColor="#FC5C32"/><stop offset=".99" stopColor="#EE2017"/></linearGradient>
        <linearGradient id="plb" x1="34.003" x2="43.536" y1="29.264" y2="4.511" gradientUnits="userSpaceOnUse"><stop stopColor="#D0E6FD"/><stop offset=".57" stopColor="#FC5C32"/><stop offset=".99" stopColor="#EE2017"/></linearGradient>
        <clipPath id="plc"><path fill="#fff" d="M0 0h45v47H0z"/></clipPath>
      </defs>
    </svg>
  );
}

// ─── Typewriter search bar ────────────────────────────────────────────────────
function SearchBar() {
  const [qIdx, setQIdx] = useState(0);
  const [shown, setShown] = useState("");
  const [typing, setTyping] = useState(true);

  useEffect(() => {
    const target = SEARCH_QUERIES[qIdx];
    if (typing) {
      if (shown.length < target.length) {
        const t = setTimeout(() => setShown(target.slice(0, shown.length + 1)), 60);
        return () => clearTimeout(t);
      } else {
        const t = setTimeout(() => setTyping(false), 1800);
        return () => clearTimeout(t);
      }
    } else {
      if (shown.length > 0) {
        const t = setTimeout(() => setShown(shown.slice(0, -1)), 30);
        return () => clearTimeout(t);
      } else {
        setQIdx(i => (i + 1) % SEARCH_QUERIES.length);
        setTyping(true);
      }
    }
  }, [shown, typing, qIdx]);

  return (
    <div style={{
      display: "flex", alignItems: "center", gap: "0.75rem",
      padding: "1.25rem 1rem 1.25rem 1.25rem",
      borderRadius: "0.625rem",
      backdropFilter: "blur(40px)",
      background: "linear-gradient(100.81deg, rgba(245,245,245,0.2) 7.89%, rgba(245,245,245,0.05) 91.16%)",
      border: "1px solid rgba(244,244,244,0.3)",
      boxShadow: "4px 5px 20px rgba(0,0,0,0.6), inset -1px -1px 4px rgba(0,0,0,0.15), inset 1px 1px 4px rgba(255,255,255,0.15)",
      maxWidth: "40.5rem", width: "100%", color: "#fff",
      fontSize: "clamp(1rem, 2vw, 1.375rem)", lineHeight: 1,
    }}>
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ flexShrink: 0, opacity: 0.7 }}>
        <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
      </svg>
      <span style={{ flex: 1, fontFamily: "'Haffer Variable', sans-serif", fontWeight: 450, letterSpacing: "-0.02em", minWidth: 0 }}>
        {shown}
        <span style={{
          display: "inline-block", width: "2px", height: "1em",
          background: "#0496ff", marginLeft: "2px", verticalAlign: "middle",
          animation: "blink 1s steps(2,start) infinite",
        }}/>
      </span>
      <div style={{
        background: "rgba(23,23,23,0.67)", border: "1px solid rgba(244,244,244,0.3)",
        borderRadius: "0.313rem", width: "1.5rem", height: "1.5rem",
        display: "flex", alignItems: "center", justifyContent: "center",
        fontSize: "0.625rem", color: "#fff", flexShrink: 0,
      }}>↵</div>
    </div>
  );
}

// ─── Scroll-reveal wrapper ────────────────────────────────────────────────────
function Reveal({ children, delay = 0, style = {}, className = "" }: { children: React.ReactNode; delay?: number; style?: React.CSSProperties; className?: string }) {
  const ref = useRef<HTMLDivElement>(null);
  const [vis, setVis] = useState(false);
  useEffect(() => {
    if (!ref.current) return;
    const obs = new IntersectionObserver(([e]) => { if (e.isIntersecting) setVis(true); }, { threshold: 0.1 });
    obs.observe(ref.current);
    return () => obs.disconnect();
  }, []);
  return (
    <div ref={ref} className={className} style={{
      opacity: vis ? 1 : 0,
      transform: vis ? "translateY(0)" : "translateY(40px)",
      transition: `opacity 0.9s ease ${delay}s, transform 0.9s ease ${delay}s`,
      ...style,
    }}>
      {children}
    </div>
  );
}

// ─── Desk Screenplay — position:fixed + scroll spacer, exact poly.app pattern ──
function DeskSection() {
  const spacerRef = useRef<HTMLDivElement>(null);
  const [phase, setPhase] = useState(-1);

  useEffect(() => {
    const onScroll = () => {
      const spacer = spacerRef.current;
      if (!spacer) return;
      const rect = spacer.getBoundingClientRect();
      const scrolled = -rect.top;
      const total = spacer.offsetHeight - window.innerHeight;
      if (scrolled < 0 || scrolled > total) { setPhase(-1); return; }
      const p = scrolled / total;
      if (p < 0.25) setPhase(0);
      else if (p < 0.5) setPhase(1);
      else if (p < 0.75) setPhase(2);
      else setPhase(3);
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  const visible = phase >= 0;

  return (
    <>
      {/* Fixed panel — always in DOM, shown/hidden by scroll */}
      <div style={{
        position: "fixed", inset: 0, zIndex: 10,
        visibility: visible ? "visible" : "hidden",
        pointerEvents: "none",
      }}>
        {/* Desk background */}
        <div style={{
          position: "absolute", backgroundImage: `url(${CDN}/images/desk/background.webp)`,
          backgroundSize: "80%", backgroundPosition: "center",
          width: "140%", height: "140%", top: "-20%", left: "-20%",
        }}/>
        <LightOverlay/>

        {/* Floating images — phase 0 */}
        <div style={{
          position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center",
          opacity: phase === 0 ? 1 : 0, transition: "opacity 0.5s ease",
        }}>
          {[...PRE_SEARCH, ...URBAN.slice(0,6), ...UPCYCLED.slice(0,6), ...FASHION.slice(0,5)].map((src, i) => (
            <img key={i} className="desk-img" src={src} alt="" style={{
              position: "absolute",
              width: i < 14 ? "16rem" : "13rem",
              height: "auto", borderRadius: "4px",
              boxShadow: "0 8px 32px rgba(0,0,0,0.6)",
              transform: `translate(${(i % 2 === 0 ? -1 : 1) * (60 + (i * 37) % 220)}px, ${((i * 53) % 180) - 90}px) rotate(${((i * 17) % 16) - 8}deg)`,
              zIndex: i,
            }}/>
          ))}
        </div>

        {/* Phase 1: text + search */}
        <div style={{
          position: "absolute", inset: 0, display: "flex", flexDirection: "column",
          alignItems: "center", justifyContent: "center", textAlign: "center",
          opacity: phase === 1 ? 1 : 0, transition: "opacity 0.5s ease",
        }}>
          <div style={{ marginBottom: "3rem" }}>
            <span className="section-title-sans">Find your files </span>
            <span className="section-title-serif">naturally.</span>
          </div>
          <p style={{ fontFamily: "'Haffer', sans-serif", fontSize: "clamp(0.875rem, 1.5vw, 1.125rem)", color: "rgba(244,244,244,0.7)", maxWidth: "36rem", lineHeight: 1.5 }}>
            Poly is a file browser that actually understands your files, down to the page, or paragraph, or pixel.
          </p>
          <div style={{ marginTop: "2.5rem", width: "90vw", maxWidth: "40.5rem" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", padding: "1.25rem 1rem 1.25rem 1.25rem", borderRadius: "0.625rem", backdropFilter: "blur(40px)", background: "linear-gradient(100.81deg, rgba(245,245,245,0.2) 7.89%, rgba(245,245,245,0.05) 91.16%)", border: "1px solid rgba(244,244,244,0.3)", boxShadow: "4px 5px 20px rgba(0,0,0,0.6)", color: "#fff", fontSize: "1.375rem" }}>
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ flexShrink: 0, opacity: 0.7 }}><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
              <span style={{ flex: 1, fontFamily: "'Haffer Variable', sans-serif", fontWeight: 450, letterSpacing: "-0.02em" }}>
                Urban Upcycled Clothing
                <span style={{ display: "inline-block", width: "2px", height: "1em", background: "#0496ff", marginLeft: "2px", verticalAlign: "middle", animation: "blink 1s steps(2,start) infinite" }}/>
              </span>
              <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                <img src={`${CDN}/images/desk/assets/search-grid/upcycled_shoot04.jpg.webp`} alt="" style={{ width: "2rem", borderRadius: "2px" }}/>
                <span style={{ fontSize: "0.875rem", opacity: 0.8 }}>upcycled_shoot04.jpg</span>
              </div>
              <div style={{ background: "rgba(23,23,23,0.67)", border: "1px solid rgba(244,244,244,0.3)", borderRadius: "0.313rem", width: "1.5rem", height: "1.5rem", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "0.625rem" }}>↵</div>
            </div>
          </div>
        </div>

        {/* Phase 2: search grid */}
        <div style={{
          position: "absolute", inset: 0, display: "flex", flexDirection: "column", alignItems: "center", paddingTop: "8rem",
          opacity: phase === 2 ? 1 : 0, transition: "opacity 0.5s ease",
        }}>
          <div style={{ textAlign: "center", marginBottom: "2rem" }}>
            <span className="section-title-sans--small">Your search doesn&apos;t just end there. </span>
            <span className="section-title-serif--small">Search by image, concept, phrase, color, face and more...</span>
          </div>
          <div style={{ display: "flex", gap: "2rem", maxWidth: "90vw" }}>
            {[SEARCH_GRID.slice(0,3), SEARCH_GRID.slice(3,6), SEARCH_GRID.slice(6,9), SEARCH_GRID.slice(9,12)].map((col, ci) => (
              <div key={ci} style={{ display: "flex", flexDirection: "column", gap: "1rem", alignItems: "center" }}>
                {col.map((item, ii) => (
                  <div key={ii} style={{ textAlign: "center" }}>
                    <div style={{ width: "16rem", outline: item.active ? "3px solid #FC5C32" : "none", borderRadius: "2px" }}>
                      <img src={item.img} alt="" style={{ width: "100%", height: "auto", display: "block", borderRadius: "2px" }}/>
                    </div>
                    <div style={{ background: item.active ? "linear-gradient(134.77deg,#f4824d 25.1%,#f42919 74.9%)" : "rgba(33,33,34,0.6)", borderRadius: "0.3rem", display: "inline-block", fontSize: "0.75rem", color: "#f4f4f4", marginTop: "0.4rem", padding: "0.25rem 0.35rem", fontFamily: "'Haffer', sans-serif" }}>{item.name}</div>
                  </div>
                ))}
              </div>
            ))}
          </div>
        </div>

        {/* Phase 3: deep results */}
        <div style={{
          position: "absolute", inset: 0, display: "flex", flexDirection: "column", alignItems: "center", paddingTop: "7rem",
          opacity: phase === 3 ? 1 : 0, transition: "opacity 0.5s ease",
        }}>
          <div style={{ textAlign: "center", marginBottom: "2rem" }}>
            <span className="section-title-sans--small">Poly can even search </span>
            <span className="section-title-serif--small">within your files, </span>
            <span className="section-title-sans--small">for that exact scene, page, or clip.</span>
          </div>
          <div style={{ display: "flex", gap: "2rem", maxWidth: "90vw" }}>
            {[SEARCH_RESULTS.slice(0,3), SEARCH_RESULTS.slice(3,6), SEARCH_RESULTS.slice(6,9), SEARCH_RESULTS.slice(9,12)].map((col, ci) => (
              <div key={ci} style={{ display: "flex", flexDirection: "column", gap: "1rem", alignItems: "center" }}>
                {col.map((item, ii) => (
                  <div key={ii} style={{ textAlign: "center" }}>
                    <div style={{ width: "16rem", outline: (item as any).active ? "3px solid #FC5C32" : "none", borderRadius: "2px" }}>
                      <img src={item.img} alt="" style={{ width: "100%", height: "auto", display: "block", borderRadius: "2px" }}/>
                    </div>
                    <div style={{ background: "rgba(33,33,34,0.6)", borderRadius: "0.3rem", display: "inline-block", fontSize: "0.75rem", color: "#f4f4f4", marginTop: "0.4rem", padding: "0.25rem 0.35rem", fontFamily: "'Haffer', sans-serif" }}>{item.name}</div>
                  </div>
                ))}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Scroll spacer — gives the fixed panel its scroll duration */}
      <div ref={spacerRef} style={{ height: "900vh" }}/>
    </>
  );
}

// ─── Light Flicker Overlay ─────────────────────────────────────────────────────
function LightOverlay() {
  const lights = [
    `${CDN}/images/desk/light-1.webp`,
    `${CDN}/images/desk/light-2.webp`,
    `${CDN}/images/desk/light-3.webp`,
  ];
  const anims = ["light1", "light2", "light3"];
  const delays = ["0s", "1.665s", "3.33s"];

  return (
    <>
      {/* Shadow layer */}
      <div style={{ position: "fixed", width: "130%", height: "130%", top: "-15%", left: "-15%", zIndex: 100, pointerEvents: "none", mixBlendMode: "multiply", opacity: 0.7 }}>
        {lights.map((src, i) => (
          <div key={i} style={{
            backgroundImage: `url(${src})`, backgroundSize: "cover",
            position: "absolute", inset: 0,
            animationName: anims[i], animationDuration: "5s",
            animationDelay: delays[i], animationIterationCount: "infinite",
            animationTimingFunction: "ease-in-out", animationFillMode: "both",
          }}/>
        ))}
      </div>
      {/* Light layer */}
      <div style={{ position: "fixed", width: "130%", height: "130%", top: "-15%", left: "-15%", zIndex: 110, pointerEvents: "none", mixBlendMode: "overlay", opacity: 0.6 }}>
        {lights.map((src, i) => (
          <div key={i} style={{
            backgroundImage: `url(${src})`, backgroundSize: "cover",
            position: "absolute", inset: 0,
            animationName: anims[i], animationDuration: "5s",
            animationDelay: delays[i], animationIterationCount: "infinite",
            animationTimingFunction: "ease-in-out", animationFillMode: "both",
          }}/>
        ))}
      </div>
    </>
  );
}


// ─── Showcase slides — sticky+scroll-phase matching poly.app ─────────────────
// ─── Showcase slides — position:fixed + scroll spacer, exact poly.app pattern ──
function ShowcaseSection() {
  const spacerRef = useRef<HTMLDivElement>(null);
  const [active, setActive] = useState(-1);
  const videoRefs = useRef<(HTMLVideoElement | null)[]>([]);

  useEffect(() => {
    const onScroll = () => {
      const spacer = spacerRef.current;
      if (!spacer) return;
      const rect = spacer.getBoundingClientRect();
      const scrolled = -rect.top;
      const total = spacer.offsetHeight - window.innerHeight;
      
      // Hide completely if out of scroll bounds
      if (scrolled < 0 || scrolled > total) {
        setActive(-1);
        return;
      }
      
      const p = Math.max(0, Math.min(1, scrolled / total));
      setActive(Math.min(SHOWCASE_SLIDES.length - 1, Math.floor(p * SHOWCASE_SLIDES.length)));
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    
    // Check initial scroll position
    onScroll();
    
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  useEffect(() => {
    videoRefs.current.forEach((v, i) => {
      if (!v) return;
      if (i === active) { v.play().catch(() => {}); }
      else { v.pause(); }
    });
  }, [active]);

  const visible = active >= 0;
  // Fallback to index 0 to avoid crashing when active is -1
  const slide = SHOWCASE_SLIDES[Math.max(0, active)];

  return (
    <>
      {/* Fixed panel — shown/hidden based on scroll */}
      <div style={{
        position: "fixed", inset: 0, zIndex: 10,
        visibility: visible ? "visible" : "hidden",
        display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: "2.75rem", padding: "0 2rem",
        // pointerEvents: visible ? "auto" : "none" // Toggle if you have interactive elements inside
      }}>
        {/* Heading */}
        <div style={{ fontSize: "clamp(1rem, 2vw, 2rem)", lineHeight: 1.1, color: "#fff", textAlign: "center", maxWidth: "60rem" }}>
          <span style={{ fontFamily: "'Haffer Variable', sans-serif", fontWeight: 450, letterSpacing: "-0.02em" }}>{slide.sans}</span>
          <span style={{ fontFamily: "'Bogue', serif", letterSpacing: "-0.03em" }}>{slide.serif}</span>
          <AnimDrawing name="line" style={{ width: "100%", height: "0.625rem", marginTop: "-0.25rem" }}/>
        </div>

        {/* Video */}
        <div style={{
          width: "min(62.5rem, 90vw)", aspectRatio: "1000/564",
          borderRadius: "8px", overflow: "hidden",
          border: "1px solid rgba(244,244,244,0.3)", background: "#111",
          position: "relative",
        }}>
          {SHOWCASE_SLIDES.map((s, i) => (
            <video
              key={s.video}
              ref={el => { videoRefs.current[i] = el; }}
              src={s.video}
              muted loop playsInline
              style={{
                position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "cover",
                opacity: i === active ? 1 : 0, transition: "opacity 0.5s ease",
              }}
            />
          ))}
        </div>

        {/* Tags */}
        <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "center", gap: "0.5rem", alignItems: "center" }}>
          <div style={{ fontFamily: "'Bogue', serif", fontSize: "clamp(1rem,1.5vw,1.5rem)", color: "#fff", marginRight: "0.5rem" }}>Perfect for:</div>
          {slide.tags.map(tag => (
            <span key={tag} style={{ border: "1px solid rgba(244,244,244,0.3)", borderRadius: "100px", padding: "0.75rem 1rem", fontSize: "0.875rem", color: "#fff", fontFamily: "'Haffer', sans-serif" }}>{tag}</span>
          ))}
        </div>

        {/* Dots */}
        <div style={{ display: "flex", gap: "6px" }}>
          {SHOWCASE_SLIDES.map((_, i) => (
            <div key={i} style={{ width: 6, height: 6, borderRadius: "50%", background: i === active ? "#FC5C32" : "rgba(244,244,244,0.3)", transition: "background 0.3s" }}/>
          ))}
        </div>
      </div>

      {/* Scroll spacer */}
      <div ref={spacerRef} style={{ height: `${SHOWCASE_SLIDES.length * 100}vh` }} />
    </>
  );
}

// ─── iPad View Modes — sticky+scroll-phase matching poly.app ─────────────────
// ─── iPad View Modes — position:fixed + scroll spacer, exact poly.app pattern ──
function ViewModesSection() {
  const spacerRef = useRef<HTMLDivElement>(null);
  const [activeMode, setActiveMode] = useState(-1);

  useEffect(() => {
    const onScroll = () => {
      const spacer = spacerRef.current;
      if (!spacer) return;
      const rect = spacer.getBoundingClientRect();
      const scrolled = -rect.top;
      const total = spacer.offsetHeight - window.innerHeight;
      
      // Hide completely if out of scroll bounds
      if (scrolled < 0 || scrolled > total) {
        setActiveMode(-1);
        return;
      }
      
      const p = Math.max(0, Math.min(1, scrolled / total));
      setActiveMode(Math.min(VIEW_MODES.length - 1, Math.floor(p * VIEW_MODES.length)));
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    
    // Check initial scroll position
    onScroll();
    
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  const visible = activeMode >= 0;

  return (
    <>
      {/* Fixed panel — shown/hidden based on scroll */}
      <div style={{
        position: "fixed", inset: 0, zIndex: 10, overflow: "hidden",
        visibility: visible ? "visible" : "hidden",
      }}>
        {/* Background image */}
        <div style={{ position: "absolute", width: "175%", height: "175%", top: "-20%", left: "-10%", transform: "rotate(5deg)", zIndex: 0, pointerEvents: "none" }}>
          <img src={`${CDN}/images/placeholder-viewmodes-background.webp`} alt="" style={{ width: "100%", height: "100%", objectFit: "contain" }}/>
        </div>

        {/* Text left */}
        <div style={{ position: "absolute", top: "10rem", left: "7rem", zIndex: 10, maxWidth: "32rem" }}>
          <div style={{ marginBottom: "0.5rem" }}>
            <span className="section-title-sans" style={{ display: "block" }}>Your media in all </span>
            <span className="section-title-serif">its glory.</span>
            <AnimDrawing name="crown" style={{ width: "6rem", height: "6rem", position: "absolute", top: "-2.25rem", right: "-3.75rem" }}/>
          </div>
          <div style={{ marginTop: "2rem", maxWidth: "18rem" }}>
            <span className="section-title-sans" style={{ fontSize: "clamp(1rem,2vw,1.5rem)" }}>with beautiful, </span>
            <span className="section-title-serif" style={{ fontSize: "clamp(1rem,2vw,1.5rem)" }}>view modes </span>
            <span className="section-title-sans" style={{ fontSize: "clamp(1rem,2vw,1.5rem)" }}>at your fingertips.</span>
          </div>

          {/* Mode icons */}
          <div style={{ display: "flex", gap: "2rem", marginTop: "4rem", flexWrap: "wrap" }}>
            {VIEW_MODES.map((m, i) => (
              <div key={m.label} style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "0.5rem", opacity: i === activeMode ? 1 : 0.4, transition: "opacity 0.3s" }}>
                <div style={{
                  width: "1.5rem", height: "1.5rem",
                  background: i === activeMode ? "linear-gradient(134.77deg, #f4824d 25.1%, #f42919 74.9%)" : "rgba(244,244,244,0.3)",
                  borderRadius: "4px", transition: "background 0.3s",
                }}/>
                <span style={{ fontSize: "0.75rem", color: "#fff", fontFamily: "'Haffer', sans-serif" }}>{m.label}</span>
              </div>
            ))}
          </div>
        </div>

        {/* iPad mockup right */}
        <div style={{
          position: "absolute", right: "8rem", top: "50%",
          transform: "translateY(-50%) rotate(1.5deg)",
          width: "55%", maxWidth: "46rem",
          zIndex: 10,
          aspectRatio: "1160/888",
          border: "1.5px solid rgba(244,244,244,0.15)",
          borderRadius: "2%", overflow: "hidden",
          boxShadow: "0 32px 64px rgba(0,0,0,0.5)",
        }}>
          <div style={{ position: "absolute", inset: "0.5%", borderRadius: "1.5%", overflow: "hidden" }}>
            {VIEW_MODES.map((m, i) => (
              <img key={m.label} src={m.img} alt={m.label} style={{
                position: "absolute", inset: 0, width: "100%", height: "100%",
                objectFit: "cover", borderRadius: "1%",
                opacity: i === activeMode ? 1 : 0,
                transition: "opacity 0.6s ease",
              }}/>
            ))}
          </div>
        </div>
      </div>
      
      {/* Scroll spacer */}
      <div ref={spacerRef} style={{ height: "500vh" }}/>
    </>
  );
}

// ─── Features Grid ────────────────────────────────────────────────────────────
function FeaturesGrid() {
  return (
    <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: "1rem", maxWidth: "90vw", margin: "0 auto" }}>
      {FEATURES.map((f, i) => (
        <Reveal key={f.title} delay={i * 0.04}>
          <div style={{
            position: "relative", height: "16rem", borderRadius: "0.5rem",
            overflow: "hidden", cursor: "default",
          }}
            onMouseEnter={e => { const img = e.currentTarget.querySelector<HTMLElement>(".feat-img"); if (img) img.style.transform = "scale(1.03)"; }}
            onMouseLeave={e => { const img = e.currentTarget.querySelector<HTMLElement>(".feat-img"); if (img) img.style.transform = "scale(1)"; }}
          >
            <img className="feat-img" src={f.img} alt="" style={{ position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "cover", zIndex: 0, transition: "transform 1s ease-in-out" }}/>
            <div style={{ position: "absolute", inset: 0, background: "linear-gradient(0deg,rgba(0,0,0,0.75),transparent)", zIndex: 1 }}/>
            <div style={{ position: "absolute", bottom: 0, left: 0, padding: "0.75rem", zIndex: 2, display: "flex", gap: "0.5rem" }}>
              <img src={f.icon} alt="" style={{ width: "2rem", height: "2rem", flexShrink: 0 }}/>
              <div style={{ display: "flex", flexDirection: "column", gap: "0.375rem" }}>
                <span style={{ fontFamily: "'Haffer', sans-serif", fontSize: "1rem", fontWeight: 600, color: "#fff", lineHeight: 1.1 }}>{f.title}</span>
                <span style={{ fontFamily: "'Haffer', sans-serif", fontSize: "0.8125rem", color: "rgba(244,244,244,0.7)", lineHeight: 1.3 }}>{f.desc}</span>
              </div>
            </div>
          </div>
        </Reveal>
      ))}
    </div>
  );
}

// ─── Main Page ────────────────────────────────────────────────────────────────
export default function Home() {
  const [scrolled, setScrolled] = useState(false);

  // Native smooth scroll — Lenis breaks position:sticky
  useEffect(() => {
    document.documentElement.style.scrollBehavior = "smooth";
    return () => { document.documentElement.style.scrollBehavior = ""; };
  }, []);

  // Navbar scroll
  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 60);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <>
      <style>{`
        @font-face { font-family:'Bogue'; src:url('/fonts/Bogue-Thin.otf') format('opentype'); font-weight:100 400; font-display:swap; }
        @font-face { font-family:'Haffer'; src:url('/fonts/Haffer-Regular.otf') format('opentype'); font-weight:400; font-display:swap; }
        @font-face { font-family:'Haffer Variable'; src:url('/fonts/HafferVF.ttf') format('truetype'); font-weight:100 900; font-display:swap; }

        *,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
        html{overflow-x:hidden;scroll-behavior:smooth;}
        body{background:#090909;color:#f4f4f4;overflow-x:hidden;font-family:'Haffer',sans-serif;}
        a{color:inherit;text-decoration:none;}

        .section-title-sans{font-family:'Haffer Variable',sans-serif;font-feature-settings:"ss04" 1,"liga" 1;font-weight:450;letter-spacing:-0.028em;line-height:1.05;font-size:clamp(2rem,5vw,3.75rem);color:#f4f4f4;}
        .section-title-serif{font-family:'Bogue',serif;font-weight:400;letter-spacing:-0.042em;line-height:1.05;font-size:clamp(2rem,5vw,3.75rem);color:#f4f4f4;}
        .section-title-sans--small{font-family:'Haffer Variable',sans-serif;font-weight:450;letter-spacing:-0.02em;font-size:clamp(1.25rem,3vw,2rem);color:#f4f4f4;}
        .section-title-serif--small{font-family:'Bogue',serif;font-weight:400;letter-spacing:-0.03em;font-size:clamp(1.25rem,3vw,2rem);color:#f4f4f4;}
        .general-title-sans{font-family:'Haffer',sans-serif;font-feature-settings:"ss04" 1,"liga" 1;letter-spacing:-0.02em;}

        .btn{display:inline-flex;align-items:center;justify-content:center;gap:0.5rem;padding:0.75rem 1rem;border-radius:0.625rem;font-family:'Haffer',sans-serif;font-weight:600;font-size:1rem;line-height:1.2;letter-spacing:0;cursor:pointer;transition:box-shadow 0.3s;border:none;text-decoration:none;white-space:nowrap;}
        .btn-white{backdrop-filter:blur(40px);background:linear-gradient(100.81deg,#f4f4f4 7.89%,#eaeaea 91.16%);box-shadow:2px 2px 5px rgba(0,0,0,0.2),inset -2px -2px 4px rgba(0,0,0,0.15),inset 2px 2px 4px #fff;color:#090909;}
        .btn-black{backdrop-filter:blur(40px);background:linear-gradient(100.81deg,#292930 7.89%,#19191d 91.16%);box-shadow:2px 2px 5px rgba(0,0,0,0.2),inset -2px -2px 4px rgba(0,0,0,0.15),inset 2px 2px 4px rgba(255,255,255,0.15);color:#fff;}
        .btn-orange{backdrop-filter:blur(40px);background:linear-gradient(134.77deg,#f4824d 25.1%,#f42919 74.9%);box-shadow:2px 2px 5px rgba(0,0,0,0.2),inset -2px -2px 4px rgba(0,0,0,0.15),inset 2px 2px 4px rgba(255,255,255,0.15);color:#fff;}
        .btn:hover{box-shadow:4px 4px 10px rgba(0,0,0,0.4),inset -2px -2px 4px rgba(0,0,0,0.15),inset 2px 2px 4px rgba(255,255,255,0.15);}

        .underline-link{position:relative;overflow:hidden;}
        .underline-link::after{content:'';position:absolute;bottom:0;left:-10%;width:120%;height:2px;background:currentColor;transform:translateX(-110%);transition:transform 0.3s ease;}
        .underline-link:hover::after{transform:translateX(0);}

        .file-tag{display:inline-flex;align-items:center;justify-content:center;padding:0.375rem 0.75rem;border-radius:100px;border:1px solid rgba(244,244,244,0.15);background:rgba(244,244,244,0.05);font-family:'Haffer',monospace;font-size:0.8125rem;color:rgba(244,244,244,0.6);letter-spacing:0.02em;}

        .bottom-nav{backdrop-filter:blur(40px);background:rgba(31,32,41,0.5);border:1px solid rgba(244,244,244,0.2);box-shadow:inset -1px -1px 4px rgba(0,0,0,0.15),inset 1px 1px 4px rgba(255,255,255,0.15);border-radius:1rem;display:flex;align-items:center;padding:0.375rem 0.5rem;}
        .bottom-nav-btn{display:flex;align-items:center;gap:0.5rem;padding:0.875rem 1rem;color:#fff;font-family:'Haffer',sans-serif;font-weight:600;font-size:1rem;cursor:pointer;border-radius:0.625rem;transition:background 0.3s;border:none;background:transparent;}
        .bottom-nav-btn:hover{background:rgba(0,0,0,0.25);}
        .bottom-nav-divider{width:2px;height:3.25rem;background:linear-gradient(180deg,transparent,rgba(245,245,245,0.2) 33%,rgba(245,245,245,0.2) 66%,transparent);}

        @keyframes blink{0%,50%{opacity:1;}51%,100%{opacity:0;}}
        @keyframes float{0%,100%{transform:translateY(0);}50%{transform:translateY(-6px);}}
        @keyframes light1{0%{opacity:1;transform:rotate(0);}50%{opacity:0;transform:rotate(4deg);}100%{opacity:1;transform:rotate(0);}}
        @keyframes light2{0%{opacity:1;transform:rotate(0);}50%{opacity:0;transform:rotate(-4deg);}100%{opacity:1;transform:rotate(0);}}
        @keyframes light3{0%{opacity:1;transform:rotate(0);}50%{opacity:0;transform:rotate(3.5deg);}100%{opacity:1;transform:rotate(0);}}

        ::-webkit-scrollbar{width:5px;}
        ::-webkit-scrollbar-track{background:#090909;}
        ::-webkit-scrollbar-thumb{background:rgba(244,244,244,0.12);border-radius:3px;}
      `}</style>

      <div style={{ background: "#090909", color: "#f4f4f4", minHeight: "100vh" }}>

        {/* ── NAVBAR ── */}
        <nav style={{
          position: "fixed", top: 0, left: 0, right: 0, zIndex: 999,
          display: "flex", alignItems: "center", justifyContent: "space-between",
          padding: "1.5rem 3rem",
          background: scrolled ? "rgba(9,9,9,0.85)" : "transparent",
          backdropFilter: scrolled ? "blur(20px)" : "none",
          transition: "background 0.3s, backdrop-filter 0.3s",
        }}>
          <a href="/"><PolyLogo/></a>
          <div style={{ display: "flex", alignItems: "center", gap: "1.5rem" }}>
            <a href="/login" className="underline-link" style={{ fontFamily: "'Haffer', sans-serif", fontWeight: 600, fontSize: "1rem", color: "#fff" }}>Login</a>
            <a href="/waitlist" className="btn btn-orange">Join waitlist</a>
          </div>
        </nav>

        {/* ── HERO (canvas stub) ── */}
        <section style={{ minHeight: "100vh", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", textAlign: "center", padding: "8rem 2rem 12rem", position: "relative", overflow: "hidden" }}>
          {/* BG glow blobs */}
          <div style={{ position: "absolute", top: "20%", left: "50%", transform: "translateX(-50%)", width: "700px", height: "500px", borderRadius: "50%", background: "radial-gradient(ellipse, rgba(252,92,50,0.15) 0%, transparent 70%)", pointerEvents: "none" }}/>

          {/* Hero image (canvas placeholder) */}
          <div style={{ position: "absolute", inset: 0, zIndex: 0 }}>
            <img src={`${CDN}/images/hero-loading.webp`} alt="" style={{ width: "100%", height: "100%", objectFit: "cover", opacity: 0.4 }}/>
          </div>

          <div style={{ position: "relative", zIndex: 1, display: "flex", flexDirection: "column", alignItems: "center", gap: "2rem" }}>
            <h1 style={{ lineHeight: 1.05 }}>
              <span className="section-title-sans" style={{ display: "block", fontSize: "clamp(2.5rem, 8vw, 5rem)" }}>The Intelligent</span>
              <div style={{ display: "inline-block", position: "relative" }}>
                <span className="section-title-serif" style={{ display: "block", fontSize: "clamp(2.5rem, 8vw, 5rem)" }}>File Browser</span>
                <AnimDrawing name="hero underline" style={{ position: "absolute", bottom: "-0.5rem", left: 0, width: "100%", height: "1.5rem" }}/>
              </div>
            </h1>

            <p style={{ fontFamily: "'Haffer', sans-serif", fontSize: "clamp(1rem, 2vw, 1.25rem)", color: "rgba(244,244,244,0.75)", maxWidth: "31rem", lineHeight: 1.5, letterSpacing: "-0.02em" }}>
              Store, browse, research, and organize your files with A.I. — available on web and desktop
            </p>

            <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap", justifyContent: "center" }}>
              <a href="/waitlist" className="btn btn-white">
                <svg width="18" height="18" viewBox="0 0 45 47" fill="none"><path fill="url(#hi-c)" d="M45 33.91 32.759 0l-2.156 19.58z"/><defs><linearGradient id="hi-c" x1="30.603" x2="45" y1="16.953" y2="16.953" gradientUnits="userSpaceOnUse"><stop stopColor="#FC5C32"/><stop offset="1" stopColor="#EE2017"/></linearGradient></defs></svg>
                Download Poly
              </a>
              <a href="/watch-demo" className="btn btn-black" target="_blank">
                <svg width="12" height="12" viewBox="0 0 12 12" fill="currentColor"><path d="M2 1l9 5-9 5V1z"/></svg>
                Watch Video
              </a>
            </div>

            <SearchBar/>
          </div>

          {/* File types belt */}
          <div style={{ position: "absolute", bottom: "2.5rem", left: 0, right: 0, display: "flex", flexDirection: "column", alignItems: "center", gap: "1rem" }}>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "0.625rem", justifyContent: "center", maxWidth: "800px", padding: "0 2rem" }}>
              {FILE_TYPES.map(t => <span key={t} className="file-tag">.{t}</span>)}
            </div>
          </div>

          {/* Scroll indicator */}
          <div style={{ position: "absolute", bottom: "6rem", left: "50%", transform: "translateX(-50%)", display: "flex", flexDirection: "column", alignItems: "center", gap: "0.5rem", color: "#fff", fontSize: "1rem", fontFamily: "'Haffer', sans-serif", opacity: 0.6, zIndex: 1 }}>
            <span>Scroll to explore</span>
            <div style={{
              backdropFilter: "blur(40px)",
              background: "linear-gradient(100.81deg, rgba(41,41,48,0.2) 7.89%, rgba(25,25,29,0.2) 91.16%)",
              border: "1px solid rgba(41,41,48,0.3)", borderRadius: "4px",
              width: "1.5rem", height: "1.5rem",
              display: "flex", alignItems: "center", justifyContent: "center",
              animation: "float 2s ease-in-out infinite",
            }}>
              <svg width="12" height="12" viewBox="0 0 12 12" fill="currentColor"><path d="M6 8L1 3h10L6 8z"/></svg>
            </div>
          </div>
        </section>

        {/* ── DESK SCREENPLAY ── */}
        <DeskSection/>


        {/* ── FILE TYPES INTERSTITIAL ── */}
        <section style={{ padding: "7.5rem 2rem", textAlign: "center", position: "relative" }}>
          <Reveal>
            <div style={{ marginBottom: "2rem" }}>
              <span className="section-title-sans">It works with nearly every file type </span>
              <span className="section-title-serif">imaginable. </span>
              <span className="section-title-sans">zip</span>
            </div>
          </Reveal>
          <Reveal delay={0.1}>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "0.625rem", justifyContent: "center", maxWidth: "60rem", margin: "0 auto 3rem" }}>
              {FILE_TYPES.map(t => <span key={t} className="file-tag" style={{ fontSize: "1rem", padding: "0.5rem 1rem" }}>.{t}</span>)}
            </div>
          </Reveal>
          <Reveal delay={0.2}>
            <div style={{ textAlign: "left", maxWidth: "32rem", margin: "0 auto" }}>
              <span className="section-title-sans" style={{ fontSize: "clamp(1.25rem,3vw,2.5rem)" }}>Transform the way you see </span>
              <span className="section-title-serif" style={{ fontSize: "clamp(1.25rem,3vw,2.5rem)" }}>your </span>
              <span className="section-title-sans" style={{ fontSize: "clamp(1.25rem,3vw,2.5rem)" }}>files...</span>
            </div>
          </Reveal>
          {/* Floating file type labels */}
          {[
            { label: "audio", top: "20%", left: "5%", name: "audio" },
            { label: "images", top: "10%", right: "5%", name: "images" },
            { label: "videos", bottom: "20%", left: "8%", name: "videos" },
            { label: "documents", bottom: "10%", right: "8%", name: "documents" },
          ].map(({ label, name, ...pos }) => (
            <AnimDrawing key={label} name={name} style={{
              position: "absolute", width: "8rem", height: "4rem", ...pos,
            }}/>
          ))}
        </section>

        {/* ── VIEW MODES / iPAD ── */}
        <ViewModesSection/>

        {/* ── SHOWCASE ── */}
        <section style={{ background: "#090909" }}>
          <ShowcaseSection/>
        </section>

        {/* ── FEATURES ── */}
        <section style={{ padding: "7.5rem 2rem", background: "#090909" }}>
          <Reveal>
            <h2 style={{ textAlign: "center", marginBottom: "3.75rem", fontSize: "clamp(1.875rem,3.5vw,3.125rem)", lineHeight: 1.1 }}>
              <span className="general-title-sans" style={{ color: "#fff" }}>All the features you&apos;d expect, </span>
              <span className="section-title-serif" style={{ fontSize: "inherit" }}>and then some.</span>
            </h2>
          </Reveal>
          <FeaturesGrid/>
        </section>

        {/* ── CTA ── */}
        <section style={{ padding: "10rem 2rem 6rem", textAlign: "center", position: "relative", overflow: "hidden" }}>
          <div style={{ position: "absolute", top: "50%", left: "50%", transform: "translate(-50%,-50%)", width: "700px", height: "400px", borderRadius: "50%", background: "radial-gradient(ellipse, rgba(252,92,50,0.12) 0%, transparent 65%)", pointerEvents: "none" }}/>
          <Reveal>
            <h2 style={{ marginBottom: "1rem", fontSize: "clamp(1.875rem,4vw,3.75rem)", lineHeight: 1.05 }}>
              <span className="general-title-sans" style={{ color: "#fff" }}>Coming to a desktop </span>
              <span className="section-title-serif" style={{ fontSize: "inherit" }}>near you.</span>
              <AnimDrawing name="rl underline" style={{ width: "40%", height: "1.5rem", margin: "-0.5rem auto 0", display: "block" }}/>
            </h2>
            <p style={{ fontFamily: "'Haffer', sans-serif", fontSize: "1.125rem", color: "rgba(244,244,244,0.55)", maxWidth: "30rem", margin: "1.5rem auto 3rem", lineHeight: 1.6 }}>
              Poly is evolving every week — join the beta and be part of what comes next.
            </p>
            <div style={{ display: "flex", gap: "1rem", justifyContent: "center", flexWrap: "wrap" }}>
              <a href="/waitlist" className="btn btn-orange">Join waitlist</a>
              <a href="/join-discord" className="btn btn-black" target="_blank">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M20.317 4.37a19.791 19.791 0 0 0-4.885-1.515.074.074 0 0 0-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 0 0-5.487 0 12.64 12.64 0 0 0-.617-1.25.077.077 0 0 0-.079-.037A19.736 19.736 0 0 0 3.677 4.37a.07.07 0 0 0-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 0 0 .031.057 19.9 19.9 0 0 0 5.993 3.03.078.078 0 0 0 .084-.028c.462-.63.874-1.295 1.226-1.994a.076.076 0 0 0-.041-.106 13.107 13.107 0 0 1-1.872-.892.077.077 0 0 1-.008-.128 10.2 10.2 0 0 0 .372-.292.074.074 0 0 1 .077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 0 1 .078.01c.12.098.246.198.373.292a.077.077 0 0 1-.006.127 12.299 12.299 0 0 1-1.873.892.077.077 0 0 0-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 0 0 .084.028 19.839 19.839 0 0 0 6.002-3.03.077.077 0 0 0 .032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 0 0-.031-.03z"/></svg>
                Join our discord
              </a>
            </div>
          </Reveal>
        </section>

        {/* ── FOOTER ── */}
        <footer style={{ padding: "2.5rem 3rem", borderTop: "1px solid rgba(244,244,244,0.06)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "1.25rem", maxWidth: "80rem", margin: "0 auto" }}>
            <div style={{ display: "flex", gap: "0.5rem", alignItems: "center", flexWrap: "wrap" }}>
              <span style={{ fontFamily: "'Bogue', serif", fontSize: "2rem", fontWeight: 400, letterSpacing: "-0.03em", color: "#fff" }}>Preserve human knowledge</span>
              <img src={`${CDN}/images/logo-minimal.png`} alt="" style={{ width: "2.25rem", objectFit: "contain" }}/>
              <span style={{ fontFamily: "'Haffer', sans-serif", fontSize: "2rem", letterSpacing: "-0.02em", color: "#fff" }}>with Poly.</span>
            </div>
            <div style={{ display: "flex", gap: "1.5rem", alignItems: "center", flexWrap: "wrap" }}>
              {["Support","Privacy","Contact"].map(item => (
                <a key={item} href="#" className="underline-link" style={{ opacity: 0.6, fontSize: "0.875rem", fontFamily: "'Haffer', sans-serif", fontWeight: 600, color: "#fff" }}>{item}</a>
              ))}
              <a href="/twitter" target="_blank" aria-label="Twitter" style={{ color: "rgba(244,244,244,0.6)", display: "flex" }}>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-4.714-6.231-5.401 6.231H2.744l7.73-8.835L1.254 2.25H8.08l4.253 5.622zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
              </a>
              <a href="/join-discord" target="_blank" aria-label="Discord" style={{ color: "rgba(244,244,244,0.6)", display: "flex" }}>
                <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor"><path d="M20.317 4.37a19.791 19.791 0 0 0-4.885-1.515.074.074 0 0 0-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 0 0-5.487 0 12.64 12.64 0 0 0-.617-1.25.077.077 0 0 0-.079-.037A19.736 19.736 0 0 0 3.677 4.37a.07.07 0 0 0-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 0 0 .031.057 19.9 19.9 0 0 0 5.993 3.03.078.078 0 0 0 .084-.028c.462-.63.874-1.295 1.226-1.994a.076.076 0 0 0-.041-.106 13.107 13.107 0 0 1-1.872-.892.077.077 0 0 1-.008-.128 10.2 10.2 0 0 0 .372-.292.074.074 0 0 1 .077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 0 1 .078.01c.12.098.246.198.373.292a.077.077 0 0 1-.006.127 12.299 12.299 0 0 1-1.873.892.077.077 0 0 0-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 0 0 .084.028 19.839 19.839 0 0 0 6.002-3.03.077.077 0 0 0 .032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 0 0-.031-.03z"/></svg>
              </a>
            </div>
          </div>
          <div style={{ textAlign: "center", marginTop: "2rem", paddingTop: "1.5rem", borderTop: "1px solid rgba(244,244,244,0.06)" }}>
            <PolyLogo/>
          </div>
        </footer>

        {/* ── BOTTOM NAV PILL ── */}
        <div style={{ position: "fixed", bottom: "1.5rem", left: "50%", transform: "translateX(-50%)", zIndex: 999 }}>
          <div className="bottom-nav">
            <button className="bottom-nav-btn">
              <img src={`${CDN}/images/icon-logo.png`} alt="" style={{ width: "1.125rem", height: "1.75rem", filter: "grayscale(100%)" }}/>
              Discover
            </button>
            <div className="bottom-nav-divider"/>
            <button className="bottom-nav-btn">
              <img src={`${CDN}/images/icon-sparkle.png`} alt="" style={{ width: "1.25rem", height: "1.5rem", filter: "grayscale(100%)" }}/>
              Showcase
            </button>
            <div className="bottom-nav-divider"/>
            <button className="bottom-nav-btn">
              <img src={`${CDN}/images/icon-ball.png`} alt="" style={{ width: "1.375rem", height: "1.375rem", filter: "grayscale(100%)" }}/>
              Features
            </button>
          </div>
        </div>

      </div>
    </>
  );
}