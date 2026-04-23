export default function Card({ title, children, headerColor = "bg-gray-600", contentColor = "bg-gray-50" }) {
  return (
    <div className="rounded-lg shadow-md hover:shadow-lg transition-all overflow-hidden">
      {/* Header Section */}
      <div className={`${headerColor} px-4 py-2.5`}>
        <h2 className="text-lg font-semibold text-black">{title}</h2>
      </div>
      
      {/* Divider Line */}
      <div className="h-px bg-gray-300"></div>
      
      {/* Content Section */}
      <div className={`${contentColor} px-4 py-3`}>
        {children}
      </div>
    </div>
  );
}
