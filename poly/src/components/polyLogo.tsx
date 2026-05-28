import React from "react";

interface PolyLogoProps {
  className?: string;
  style?: React.CSSProperties;
}

export function PolyLogo({ className, style }: PolyLogoProps) {
  return (
    <svg
      width="138"
      height="47"
      viewBox="0 0 138 47"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      style={{ width: "8.625rem", height: "3rem", ...style }}
    >
      <path
        fill="#fff"
        d="M59.08 38.902V8.039h12.345c6.04 0 10.008 3.66 10.008 9.171 0 5.6-3.968 9.215-10.008 9.215h-7.187v12.477zm5.158-16.886h6.658c3.262 0 5.379-1.896 5.379-4.806 0-2.866-2.117-4.718-5.38-4.718h-6.657zm28.979 17.239c-6.658 0-11.463-4.806-11.463-11.508s4.805-11.419 11.463-11.419 11.463 4.718 11.463 11.42c0 6.745-4.806 11.507-11.463 11.507m0-4.145c3.88 0 6.57-2.998 6.57-7.363 0-4.276-2.69-7.274-6.57-7.274-3.836 0-6.57 2.954-6.57 7.274 0 4.365 2.734 7.363 6.57 7.363m20.809 4.145c-3.791 0-6.304-2.073-6.304-6.922V7.687h4.805v24.425c0 2.16.838 2.91 2.249 2.91a6.1 6.1 0 0 0 2.292-.44v4.1c-.661.308-1.895.573-3.042.573m6.618 7.671 3.483-8.333-8.686-21.912h5.203l5.996 15.74 5.952-15.74h5.07l-11.948 30.245z"
      />
      <g clipPath="url(#poly-logo-clip)">
        <path fill="url(#poly-grad-b)" d="m30.538 19.612 14.299 13.81L32.64.3z" opacity=".5" />
        <path fill="url(#poly-grad-c)" d="M45 33.91 32.759 0l-2.156 19.58z" />
        <path fill="url(#poly-grad-d)" d="M24.148 29.576 45 33.91 30.603 19.58z" />
        <path fill="url(#poly-grad-e)" d="M30.603 19.58 32.759 0 21.71 17.838l8.892 1.741Z" />
        <path fill="url(#poly-grad-f)" d="M0 13.585 12.848 47l2.702-19.215z" />
        <path fill="url(#poly-grad-g)" d="M32.759 0 0 13.585l21.712 4.253z" />
        <path fill="url(#poly-grad-h)" d="M24.148 29.576 12.848 47 45 33.91z" />
        <path fill="url(#poly-grad-i)" d="M15.55 27.785 12.848 47l11.3-17.424-8.598-1.79Z" />
        <path fill="url(#poly-grad-j)" d="M21.712 17.838 0 13.585l15.55 14.2 8.598 1.79 6.455-9.996-8.892-1.74Z" />
      </g>
      <defs>
        <linearGradient id="poly-grad-c" x1="30.603" x2="45" y1="16.953" y2="16.953" gradientUnits="userSpaceOnUse">
          <stop stopColor="#FFBA84"/><stop offset=".57" stopColor="#FC5C32"/><stop offset=".99" stopColor="#EE2017"/>
        </linearGradient>
        <linearGradient id="poly-grad-d" x1="40.868" x2="26.463" y1="38.069" y2="23.741" gradientUnits="userSpaceOnUse">
          <stop stopColor="#FFBA84"/><stop offset=".57" stopColor="#FC5C32"/><stop offset=".99" stopColor="#EE2017"/>
        </linearGradient>
        <linearGradient id="poly-grad-e" x1="27.233" x2="27.233" y1="19.579" y2="0" gradientUnits="userSpaceOnUse">
          <stop stopColor="#FFBA84"/><stop offset=".57" stopColor="#FC5C32"/><stop offset=".99" stopColor="#EE2017"/>
        </linearGradient>
        <linearGradient id="poly-grad-f" x1="0" x2="15.55" y1="30.293" y2="30.293" gradientUnits="userSpaceOnUse">
          <stop stopColor="#FFBA84"/><stop offset=".57" stopColor="#FC5C32"/><stop offset=".99" stopColor="#EE2017"/>
        </linearGradient>
        <linearGradient id="poly-grad-g" x1="16.377" x2="16.377" y1="17.838" y2="0" gradientUnits="userSpaceOnUse">
          <stop stopColor="#FFBA84"/><stop offset=".57" stopColor="#FC5C32"/><stop offset=".99" stopColor="#EE2017"/>
        </linearGradient>
        <linearGradient id="poly-grad-h" x1="16.125" x2="38.83" y1="50.294" y2="27.707" gradientUnits="userSpaceOnUse">
          <stop stopColor="#FFBA84"/><stop offset=".57" stopColor="#FC5C32"/><stop offset=".99" stopColor="#EE2017"/>
        </linearGradient>
        <linearGradient id="poly-grad-i" x1="18.496" x2="18.496" y1="47" y2="27.785" gradientUnits="userSpaceOnUse">
          <stop stopColor="#FFBA84"/><stop offset=".57" stopColor="#FC5C32"/><stop offset=".99" stopColor="#EE2017"/>
        </linearGradient>
        <linearGradient id="poly-grad-j" x1="15.302" x2="15.302" y1="29.576" y2="13.589" gradientUnits="userSpaceOnUse">
          <stop stopColor="#FFBA84"/><stop offset=".57" stopColor="#FC5C32"/><stop offset=".99" stopColor="#EE2017"/>
        </linearGradient>
        <linearGradient id="poly-grad-b" x1="34.003" x2="43.536" y1="29.264" y2="4.511" gradientUnits="userSpaceOnUse">
          <stop stopColor="#D0E6FD"/><stop offset=".57" stopColor="#FC5C32"/><stop offset=".99" stopColor="#EE2017"/>
        </linearGradient>
        <clipPath id="poly-logo-clip">
          <path fill="#fff" d="M0 0h45v47H0z"/>
        </clipPath>
      </defs>
    </svg>
  );
}