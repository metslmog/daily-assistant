export default function CommuteInfo({ commute }) {
  return (
    <div className="bg-gradient-to-br from-green-100 to-green-200 shadow-lg rounded-2xl p-6 border border-green-200 hover:shadow-2xl transition-all">
      <h2 className="text-xl font-bold mb-2 text-green-600">Commute</h2>
      <p className="text-green-700 text-lg font-medium">Mode: {commute.mode}</p>
      <p className="text-green-700 text-lg font-medium">Leave at: {commute.departure}</p>
    </div>
  );
}
