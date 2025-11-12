import { NextRequest, NextResponse } from "next/server";
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";

/**
 * Simplified entitlement route - extracts username from authenticated session.
 * 
 * The agent will handle full entitlement validation via MCP when needed.
 * This just provides the username for the frontend to pass to the agent.
 */
export async function POST(request: NextRequest) {
  try {
    const session = await getServerSession(authOptions);
    
    if (!session || !session.user?.email) {
      console.error("❌ FRONTEND API: No session or email found");
      return NextResponse.json(
        { error: "Unauthorized" },
        { status: 401 }
      );
    }

    console.log("🔍 FRONTEND API: Extracting username from session");
    console.log("📧 FRONTEND API: Session email:", session.user.email);

    // Extract username from email (e.g., kannan.velusamy@company.com -> kannan.velusamy)
    const username = session.user.email.split("@")[0];
    
    if (!username) {
      console.error("❌ FRONTEND API: Could not extract username from email");
      return NextResponse.json(
        { error: "Invalid email format" },
        { status: 400 }
      );
    }

    console.log("✅ FRONTEND API: Username extracted:", username);
    console.log("ℹ️  FRONTEND API: Full profile will be fetched by agent via MCP when needed");

    // Return basic user info
    // The agent will call entitlement_mcp to get full profile, roles, and status
    return NextResponse.json({
      data: {
        username: username,
        email: session.user.email,
        name: session.user.name,
      }
    });
    
  } catch (error: any) {
    console.error("❌ FRONTEND API: Error extracting username:", error.message);
    
    return NextResponse.json(
      { error: error.message || "Failed to extract username" },
      { status: 500 }
    );
  }
}


