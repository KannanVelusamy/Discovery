"use client";

import { useSession, signOut } from "next-auth/react";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

interface BasicUserData {
  username: string;
  email: string;
  name?: string;
}

export default function ProfileCheck() {
  const { data: session, status } = useSession();
  const router = useRouter();
  const [isChecking, setIsChecking] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [userData, setUserData] = useState<BasicUserData | null>(null);

  useEffect(() => {
    if (status === "unauthenticated") {
      router.push("/");
      return;
    }

    const extractUsername = async () => {
      try {
        console.log("🔍 FRONTEND CLIENT: Extracting username from session");
        console.log("📧 FRONTEND CLIENT: User email:", session?.user?.email);

        const response = await fetch("/api/entitlement", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || "Username extraction failed");
        }

        const data = await response.json();
        const basicData = data.data;

        if (!basicData || !basicData.username) {
          throw new Error("No username received");
        }

        console.log("✅ FRONTEND CLIENT: Username extracted successfully:");
        console.log("   - Username:", basicData.username);
        console.log("   - Email:", basicData.email);
        console.log("   - Name:", basicData.name);

        setUserData(basicData);

        // Store username in localStorage for the agent to use
        // The agent will validate full profile/roles via MCP when needed
        localStorage.setItem("userProfile", JSON.stringify({
          username: basicData.username,
          email: basicData.email,
          name: basicData.name
        }));
        console.log("💾 FRONTEND CLIENT: Username stored in localStorage");
        console.log("ℹ️  FRONTEND CLIENT: Agent will fetch full profile via MCP on first query");

        // Redirect to terms page after successful extraction
        setTimeout(() => {
          console.log("➡️ FRONTEND CLIENT: Redirecting to terms page");
          router.push("/terms");
        }, 1500);

      } catch (err: any) {
        console.error("❌ FRONTEND CLIENT: Username extraction failed:", err.message);
        setError(err.message);
        setIsChecking(false);
      }
    };

    if (status === "authenticated" && session?.user?.email) {
      extractUsername();
    }
  }, [status, session, router]);

  const handleSignOut = async () => {
    console.log("🚪 FRONTEND CLIENT: User signing out");
    localStorage.removeItem("userProfile");
    await signOut({ callbackUrl: "/" });
  };

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-red-50 via-orange-50 to-yellow-50 flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-white rounded-2xl shadow-2xl border border-gray-100 p-8">
          <div className="text-center">
            <div className="w-16 h-16 bg-red-100 rounded-full mx-auto flex items-center justify-center mb-4">
              <svg
                className="w-8 h-8 text-red-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Authentication Error
            </h2>
            <p className="text-gray-600 mb-6">{error}</p>
            <button
              onClick={handleSignOut}
              className="w-full px-6 py-3 bg-gradient-to-r from-red-600 to-orange-600 text-white rounded-xl hover:from-red-700 hover:to-orange-700 transition-all duration-200 font-semibold shadow-lg"
            >
              Sign Out
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-2xl border border-gray-100 p-8">
        <div className="text-center">
          <div className="w-16 h-16 bg-blue-100 rounded-full mx-auto flex items-center justify-center mb-4">
            {isChecking ? (
              <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600"></div>
            ) : (
              <svg
                className="w-8 h-8 text-blue-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M5 13l4 4L19 7"
                />
              </svg>
            )}
          </div>
          
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            {isChecking ? "Verifying Authentication" : "Verified"}
          </h2>
          
          <p className="text-gray-600 mb-6">
            {isChecking
              ? "Extracting your profile information..."
              : "Authentication successful! Redirecting..."}
          </p>

          {userData && !isChecking && (
            <div className="text-left bg-gray-50 rounded-lg p-4 mb-4">
              <p className="text-sm text-gray-600 mb-2">Welcome,</p>
              <p className="text-lg font-semibold text-gray-900">
                {userData.name || userData.username}
              </p>
              <p className="text-sm text-gray-600">{userData.email}</p>
              <div className="mt-3 pt-3 border-t border-gray-200">
                <p className="text-xs text-gray-500">Username: {userData.username}</p>
                <p className="text-xs text-blue-600 mt-2">
                  The agent will validate your profile and roles when you start chatting
                </p>
              </div>
            </div>
          )}

          {session?.user?.email && (
            <p className="text-xs text-gray-500">
              Authenticated as: {session.user.email}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
