export async function fetchRecommendations() {
    const res = await fetch("http://localhost:5001/api/recommendations");
    return res.json();
}