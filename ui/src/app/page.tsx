"use client";

import { useSession, signIn, signOut } from "next-auth/react";
import { useRouter } from "next/navigation";
import { Thread } from "@/components/thread";
import { StreamProvider } from "@/providers/Stream";
import { ThreadProvider } from "@/providers/Thread";
import { ArtifactProvider } from "@/components/thread/artifact";
import { Toaster } from "@/components/ui/sonner";
import React, { useEffect } from "react";

export default function DemoPage(): React.ReactNode {
  const { data: session, status } = useSession();
  const router = useRouter();

  // Check if user has accepted terms after authentication
  useEffect(() => {
    if (status === "authenticated") {
      // Check if profile has been verified
      const userProfile = localStorage.getItem("userProfile");
      
      if (!userProfile) {
        // Redirect to profile check if not done yet
        console.log("🔄 FRONTEND PAGE: No profile found, redirecting to profile-check");
        router.push("/profile-check");
        return;
      }
      
      // Check if terms have been accepted
      const termsAccepted = localStorage.getItem("termsAccepted");
      if (termsAccepted !== "true") {
        // Redirect to terms page if not accepted
        console.log("🔄 FRONTEND PAGE: Terms not accepted, redirecting to terms");
        router.push("/terms");
        return;
      }
      
      // Both checks passed, log the profile
      console.log("✅ FRONTEND PAGE: User fully authenticated and authorized");
      try {
        console.log("👤 FRONTEND PAGE: User profile:", JSON.parse(userProfile));
      } catch (error) {
        console.error("❌ FRONTEND PAGE: Failed to parse user profile", error);
      }
    }
  }, [status, router]);

  // Show loading state while checking authentication
  if (status === "loading") {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // Show sign in page if not authenticated
  if (!session) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
        <div className="text-center max-w-md p-8 bg-white rounded-2xl shadow-2xl border border-gray-100">
          <div className="mb-6">
            <div className="w-16 h-16 bg-blue-600 rounded-xl mx-auto flex items-center justify-center mb-4">
              <svg
                className="w-10 h-10 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
                />
              </svg>
            </div>
            <h1 className="text-3xl font-bold mb-2 text-gray-900">
              Discovery Agent
            </h1>
            <p className="text-sm text-gray-500">Powered by LangGraph & Azure AD</p>
          </div>
          
          <p className="text-gray-600 mb-8 leading-relaxed">
            Sign in with your Microsoft account to access the AI-powered
            conversational agent
          </p>
          
          <button
            onClick={() => signIn("azure-ad")}
            className="w-full px-6 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl hover:from-blue-700 hover:to-indigo-700 transition-all duration-200 font-semibold shadow-lg hover:shadow-xl transform hover:scale-[1.02] flex items-center justify-center gap-3"
          >
            <svg
              className="w-5 h-5"
              fill="currentColor"
              viewBox="0 0 24 24"
            >
              <path d="M11.4 24H0V12.6h11.4V24zM24 24H12.6V12.6H24V24zM11.4 11.4H0V0h11.4v11.4zm12.6 0H12.6V0H24v11.4z" />
            </svg>
            Sign in with Microsoft
          </button>
          
          <p className="mt-6 text-xs text-gray-500">
            Secure authentication powered by Microsoft Azure AD
          </p>
        </div>
      </div>
    );
  }

  // Render the main application if authenticated
  return (
    <div className="min-h-screen flex flex-col">
      {/* User info bar */}
      <div className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-3 flex justify-between items-center">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center">
                <svg
                  className="w-5 h-5 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
                  />
                </svg>
              </div>
              <span className="font-semibold text-gray-900">Discovery Agent</span>
            </div>
            <div className="hidden sm:flex items-center gap-2 pl-4 border-l border-gray-300">
              <span className="text-sm text-gray-500">Signed in as:</span>
              <span className="text-sm font-medium text-gray-900">
                {session.user?.email}
              </span>
            </div>
          </div>
                <button
                  onClick={() => {
                    console.log("🚪 FRONTEND PAGE: User signing out, clearing profile data");
                    localStorage.removeItem("userProfile");
                    localStorage.removeItem("termsAccepted");
                    signOut();
                  }}
                  className="text-sm px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors font-medium"
                >
                  Sign Out
                </button>
        </div>
      </div>

      {/* Main chat interface */}
      <div className="flex-1">
        <React.Suspense fallback={<div>Loading (layout)...</div>}>
          <Toaster />
          <ThreadProvider>
            <StreamProvider>
              <ArtifactProvider>
                <Thread />
              </ArtifactProvider>
            </StreamProvider>
          </ThreadProvider>
        </React.Suspense>
      </div>
    </div>
  );
}
