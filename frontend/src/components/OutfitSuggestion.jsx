import Card from "./Card";

export default function OutfitSuggestion({ outfit }) {
  return (
    <Card 
      title="Outfit Suggestion" 
      headerColor="bg-purple-500" 
      contentColor="bg-purple-50"
    >
      <p className="text-black text-sm font-medium whitespace-pre-line leading-relaxed">{outfit}</p>
    </Card>
  );
}