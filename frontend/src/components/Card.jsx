export default function Card({ children }) {
  return (
    //<div className="bg-white rounded-xl p-6 border hover:shadow-2xl transition-all">
    <div className="backdrop-blur-xl bg-white/20 border border-white/30 shadow-lg rounded-2xl p-6">

      {children}
    </div>
  );
}
