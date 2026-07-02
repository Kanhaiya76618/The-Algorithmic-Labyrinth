export default function Frame({ label, className = '', children, ...rest }) {
  return (
    <div className={`frame ${className}`.trim()} {...rest}>
      {label && <span className="frame__label">{label}</span>}
      <span className="frame__corner frame__corner--tl" />
      <span className="frame__corner frame__corner--tr" />
      <span className="frame__corner frame__corner--bl" />
      <span className="frame__corner frame__corner--br" />
      {children}
    </div>
  )
}
