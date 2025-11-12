"use client";

import { useSession, signOut } from "next-auth/react";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

export default function TermsAndConditions() {
  const { data: session, status } = useSession();
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    // If not authenticated, redirect to home
    if (status === "unauthenticated") {
      router.push("/");
    }

    // If already accepted terms, redirect to chat
    if (status === "authenticated" && localStorage.getItem("termsAccepted") === "true") {
      router.push("/");
    }
  }, [status, router]);

  const handleAccept = () => {
    setIsLoading(true);
    // Store acceptance in localStorage
    localStorage.setItem("termsAccepted", "true");
    // Redirect to main chat page
    router.push("/");
  };

  const handleDisagree = async () => {
    setIsLoading(true);
    // Remove any stored acceptance and profile data
    localStorage.removeItem("termsAccepted");
    localStorage.removeItem("userProfile");
    console.log("🚪 FRONTEND TERMS: User disagreed, clearing all data and signing out");
    // Sign out the user
    await signOut({ callbackUrl: "/" });
  };

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

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 flex items-center justify-center p-4">
      <div className="max-w-4xl w-full bg-white rounded-2xl shadow-2xl border border-gray-100 overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 px-8 py-6">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 bg-white/20 rounded-lg flex items-center justify-center">
              <svg
                className="w-6 h-6 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
            </div>
            <h1 className="text-3xl font-bold text-white">
              Terms and Conditions
            </h1>
          </div>
          <p className="text-blue-100">
            Please review and accept our terms to continue
          </p>
        </div>

        {/* User Info */}
        {session?.user?.email && (
          <div className="bg-blue-50 px-8 py-4 border-b border-blue-100">
            <p className="text-sm text-gray-600">
              Signed in as:{" "}
              <span className="font-semibold text-gray-900">
                {session.user.email}
              </span>
            </p>
          </div>
        )}

        {/* Content */}
        <div className="px-8 py-6 max-h-96 overflow-y-auto">
          <div className="prose prose-sm max-w-none">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Discovery Agent - Terms of Service
            </h2>

            <h3 className="text-lg font-semibold text-gray-900 mt-6 mb-2">
              1. Acceptance of Terms
            </h3>
            <p className="text-gray-700 mb-4">
              By accessing and using the Discovery Agent application, you accept
              and agree to be bound by the terms and provision of this agreement.
              If you do not agree to these terms, please click "Disagree" below.
            </p>

            <h3 className="text-lg font-semibold text-gray-900 mt-6 mb-2">
              2. Use of Service
            </h3>
            <p className="text-gray-700 mb-4">
              This AI-powered conversational agent is provided for authorized
              users only. You agree to use this service in compliance with all
              applicable laws and regulations. Misuse of the service may result
              in termination of access.
            </p>

            <h3 className="text-lg font-semibold text-gray-900 mt-6 mb-2">
              3. Data Privacy
            </h3>
            <p className="text-gray-700 mb-4">
              Your conversations with the Discovery Agent may be logged for
              quality assurance and service improvement purposes. We are
              committed to protecting your privacy and will handle your data in
              accordance with applicable data protection laws.
            </p>

            <h3 className="text-lg font-semibold text-gray-900 mt-6 mb-2">
              4. User Responsibilities
            </h3>
            <ul className="list-disc list-inside text-gray-700 mb-4 space-y-2">
              <li>
                You are responsible for maintaining the confidentiality of your
                account credentials
              </li>
              <li>
                You agree not to share sensitive or confidential information
                without proper authorization
              </li>
              <li>
                You will not use the service for any illegal or unauthorized
                purpose
              </li>
              <li>
                You will not attempt to interfere with or disrupt the service
              </li>
            </ul>

            <h3 className="text-lg font-semibold text-gray-900 mt-6 mb-2">
              5. Intellectual Property
            </h3>
            <p className="text-gray-700 mb-4">
              The Discovery Agent and all associated intellectual property rights
              remain the property of the service provider. You are granted a
              limited, non-exclusive license to use the service.
            </p>

            <h3 className="text-lg font-semibold text-gray-900 mt-6 mb-2">
              6. Disclaimer
            </h3>
            <p className="text-gray-700 mb-4">
              The service is provided "as is" without warranties of any kind. The
              AI responses are generated automatically and should be verified for
              accuracy before making important decisions based on them.
            </p>

            <h3 className="text-lg font-semibold text-gray-900 mt-6 mb-2">
              7. Changes to Terms
            </h3>
            <p className="text-gray-700 mb-4">
              We reserve the right to modify these terms at any time. Continued
              use of the service after changes constitutes acceptance of the
              modified terms.
            </p>

            <h3 className="text-lg font-semibold text-gray-900 mt-6 mb-2">
              8. Contact
            </h3>
            <p className="text-gray-700 mb-4">
              If you have questions about these terms, please contact your system
              administrator.
            </p>

            <p className="text-sm text-gray-500 mt-8 pt-4 border-t border-gray-200">
              Last updated: November 9, 2025
            </p>
          </div>
        </div>

        {/* Actions */}
        <div className="px-8 py-6 bg-gray-50 border-t border-gray-200 flex gap-4 justify-end">
          <button
            onClick={handleDisagree}
            disabled={isLoading}
            className="px-6 py-3 bg-white border-2 border-gray-300 text-gray-700 rounded-xl hover:bg-gray-50 hover:border-gray-400 transition-all duration-200 font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Disagree & Sign Out
          </button>
          <button
            onClick={handleAccept}
            disabled={isLoading}
            className="px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl hover:from-blue-700 hover:to-indigo-700 transition-all duration-200 font-semibold shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {isLoading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                Processing...
              </>
            ) : (
              <>
                <svg
                  className="w-5 h-5"
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
                I Agree & Continue
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}

