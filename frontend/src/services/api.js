export async function fetchRecommendations() {
    const res = await fetch("https://localhost:5000/recommendations");
    if (!res.ok) {
        throw new Error("Network response was not ok");
    }
    return res.json();
}