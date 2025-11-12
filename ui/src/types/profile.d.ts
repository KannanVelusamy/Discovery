/**
 * Basic user data extracted from SSO session.
 * This is stored in localStorage for the frontend to pass to the agent.
 */
export interface BasicUserData {
  username: string;
  email: string;
  name?: string;
}

/**
 * Response from /api/entitlement route.
 * Returns only basic user info extracted from session.
 */
export interface EntitlementApiResponse {
  data: BasicUserData;
}

/**
 * Full user profile from entitlement MCP.
 * This is fetched by the agent when needed, not by the frontend.
 * The agent receives this from the entitlement_mcp server.
 */
export interface FullUserProfile {
  username: string;
  email: string;
  employeeId: string;
  firstName: string;
  lastName: string;
  role: string[];
  status: string;
}

/**
 * Response from entitlement_mcp tool.
 * The agent receives this structure when calling check_user_entitlement.
 */
export interface EntitlementMcpResponse {
  data: {
    profile: FullUserProfile;
  };
}


