export const signupUser = async (credentials) => {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}auth/signup`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: 'include',
      body: JSON.stringify(credentials),
    });
  
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || "Signup failed");
    }
  
    return response.json();
  };
  