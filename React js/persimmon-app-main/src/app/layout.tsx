import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import AuthProvider from "./components/AuthProvider";
import { UploadProvider } from "./components/uploadContext";
import GlobalUpload from "./components/globalUpload";
import { Toaster } from "@/components/ui/toaster";
const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "persimmon",
  description: "next generation ATS in a persishell (as in nutshell)",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <link rel="icon" href="/images/persimmon-logo.png" type="image/png" />
        <link rel="stylesheet" href="https://unpkg.com/react-quill@2.0.0/dist/quill.snow.css" />
      </head>
      <body className={inter.className}>
        <AuthProvider>
          <UploadProvider>
            {children}
            <GlobalUpload></GlobalUpload>
          </UploadProvider>
        </AuthProvider>
        <Toaster />
      </body>
    </html>
  );
}
