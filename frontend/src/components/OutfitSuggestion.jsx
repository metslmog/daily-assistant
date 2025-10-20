import Card from "./Card";

export default function OutfitSuggestion({ outfit }) {
  return (
    <Card>
      <h2 className="text-xl font-bold mb-2 text-blue-600">Outfit Suggestion</h2>
      <p className="text-blue-700 text-lg font-medium whitespace-pre-line">{outfit}</p>
    </Card>
  );
}