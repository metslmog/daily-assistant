export default function OutfitSuggestion({ outfit }) {
  return (
    <div className="bg-gradient-to-br from-blue-100 to-blue-200 shadow-lg rounded-2xl p-6 border border-blue-200 hover:shadow-2xl transition-all">
      <h2 className="text-xl font-bold mb-2 text-blue-600">Outfit Suggestion</h2>
      <p className="text-blue-700 text-lg font-medium">{outfit}</p>
    </div>
  );
}