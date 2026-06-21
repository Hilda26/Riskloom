import Link from "next/link";
import type { AnchorHTMLAttributes, ButtonHTMLAttributes } from "react";

type Variant = "primary" | "ghost" | "light";

const VARIANT_CLASS: Record<Variant, string> = {
  primary: "btn btn-p",
  ghost: "btn btn-g",
  light: "btn-lt",
};

interface LinkButtonProps extends AnchorHTMLAttributes<HTMLAnchorElement> {
  href: string;
  variant?: Variant;
  arrow?: boolean;
}

export function LinkButton({
  href,
  variant = "primary",
  arrow = false,
  children,
  className,
  ...rest
}: LinkButtonProps) {
  return (
    <Link href={href} className={`${VARIANT_CLASS[variant]} ${className ?? ""}`} {...rest}>
      {children}
      {arrow && <span className="arr">&rarr;</span>}
    </Link>
  );
}

interface ActionButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary";
}

export function ActionButton({
  variant = "secondary",
  className,
  children,
  ...rest
}: ActionButtonProps) {
  const variantClass = variant === "primary" ? "dm-b dm-bp" : "dm-b dm-bs";
  return (
    <button className={`${variantClass} ${className ?? ""}`} {...rest}>
      {children}
    </button>
  );
}
