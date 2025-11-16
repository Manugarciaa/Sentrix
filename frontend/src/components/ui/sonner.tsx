import { useTheme } from "@/hooks/useTheme"
import { Toaster as Sonner } from "sonner"

type ToasterProps = React.ComponentProps<typeof Sonner>

const Toaster = ({ ...props }: ToasterProps) => {
  const { theme } = useTheme()

  return (
    <Sonner
      theme={theme as ToasterProps["theme"]}
      className="toaster group"
      closeButton={false}
      gap={12}
      position="top-right"
      offset="80px"
      toastOptions={{
        classNames: {
          toast:
            "group toast group-[.toaster]:border-2 group-[.toaster]:shadow-lg group-[.toaster]:py-2.5 group-[.toaster]:px-3.5 group-[.toaster]:min-h-0 group-[.toaster]:rounded-lg group-[.toaster]:backdrop-blur-sm",
          description: "group-[.toast]:text-xs group-[.toast]:mt-0.5 group-[.toast]:opacity-90 group-[.toast]:leading-tight",
          actionButton:
            "group-[.toast]:bg-primary group-[.toast]:text-primary-foreground group-[.toast]:rounded group-[.toast]:px-2 group-[.toast]:py-1 group-[.toast]:text-xs group-[.toast]:font-semibold group-[.toast]:hover:bg-primary/90",
          cancelButton:
            "group-[.toast]:bg-muted group-[.toast]:text-muted-foreground group-[.toast]:rounded group-[.toast]:px-2 group-[.toast]:py-1 group-[.toast]:text-xs",
          closeButton:
            "group-[.toast]:bg-transparent group-[.toast]:border-0 group-[.toast]:hover:bg-black/5 dark:group-[.toast]:hover:bg-white/10 group-[.toast]:rounded group-[.toast]:w-5 group-[.toast]:h-5 group-[.toast]:opacity-80 group-[.toast]:hover:opacity-100 group-[.toast]:transition-opacity",
          title: "group-[.toast]:font-bold group-[.toast]:text-sm group-[.toast]:leading-tight",
          // SUCCESS - Verde distintivo
          success:
            "group-[.toaster]:bg-emerald-50 group-[.toaster]:text-emerald-900 group-[.toaster]:border-emerald-400 " +
            "dark:group-[.toaster]:bg-emerald-950/95 dark:group-[.toaster]:text-emerald-50 dark:group-[.toaster]:border-emerald-600 " +
            "[&_[data-description]]:text-emerald-700 dark:[&_[data-description]]:text-emerald-200 " +
            "[&_[data-icon]]:text-emerald-600 dark:[&_[data-icon]]:text-emerald-400",
          // ERROR - Rojo distintivo
          error:
            "group-[.toaster]:bg-red-50 group-[.toaster]:text-red-900 group-[.toaster]:border-red-400 " +
            "dark:group-[.toaster]:bg-red-950/95 dark:group-[.toaster]:text-red-50 dark:group-[.toaster]:border-red-600 " +
            "[&_[data-description]]:text-red-700 dark:[&_[data-description]]:text-red-200 " +
            "[&_[data-icon]]:text-red-600 dark:[&_[data-icon]]:text-red-400",
          // WARNING - Naranja/Amber distintivo
          warning:
            "group-[.toaster]:bg-orange-50 group-[.toaster]:text-orange-900 group-[.toaster]:border-orange-400 " +
            "dark:group-[.toaster]:bg-orange-950/95 dark:group-[.toaster]:text-orange-50 dark:group-[.toaster]:border-orange-600 " +
            "[&_[data-description]]:text-orange-700 dark:[&_[data-description]]:text-orange-200 " +
            "[&_[data-icon]]:text-orange-600 dark:[&_[data-icon]]:text-orange-400",
          // INFO - Azul distintivo
          info:
            "group-[.toaster]:bg-sky-50 group-[.toaster]:text-sky-900 group-[.toaster]:border-sky-400 " +
            "dark:group-[.toaster]:bg-sky-950/95 dark:group-[.toaster]:text-sky-50 dark:group-[.toaster]:border-sky-600 " +
            "[&_[data-description]]:text-sky-700 dark:[&_[data-description]]:text-sky-200 " +
            "[&_[data-icon]]:text-sky-600 dark:[&_[data-icon]]:text-sky-400",
        },
      }}
      {...props}
    />
  )
}

export { Toaster }
