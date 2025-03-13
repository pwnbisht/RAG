export const logoutUser = async () => {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}auth/logout`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: 'include',
    });
  
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || "Logout failed");
    }
  
    return response.json();
  };
  