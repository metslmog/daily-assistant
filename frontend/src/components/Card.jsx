export default function Card({ children }) {
  return (
    <div className="bg-white rounded-xl p-6 border hover:shadow-2xl transition-all">
      {children}
    </div>
  );
}
