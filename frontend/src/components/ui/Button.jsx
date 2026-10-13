const base =
  "inline-flex items-center justify-center gap-1.5 rounded-lg border font-semibold cursor-pointer disabled:cursor-not-allowed disabled:opacity-50";

const variants = {
  default: "border-line bg-white text-ink hover:bg-panel",
  primary: "border-brand bg-brand text-white hover:bg-brand-deep",
  danger: "border-[#e4b3ae] bg-white text-bad hover:bg-bad-wash",
  ghost: "border-transparent bg-transparent text-brand hover:bg-panel",
};

const sizes = {
  normal: "px-3.5 py-2 text-sm",
  small: "px-2.5 py-1 text-[13px]",
};

export default function Button({
  variant = "default",
  size = "normal",
  type = "button",
  className = "",
  ...props
}) {
  return (
    <button
      type={type}
      className={`${base} ${variants[variant]} ${sizes[size]} ${className}`}
      {...props}
    />
  );
}
