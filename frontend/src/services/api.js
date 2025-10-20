export async function fetchRecommendations(home, work) {
    const res = await fetch(`http://localhost:5001/api/recommendations?home=${home}&work=${work}`);
    if (!res.ok) throw new Error("Failed to fetch recommendations");
    return await res.json();
}