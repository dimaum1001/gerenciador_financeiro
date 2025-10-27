import { toast } from "sonner"

export function useToast() {
  return {
    toast: ({ title, description, variant } = {}) => {
      const message = [title, description].filter(Boolean).join(" - ")
      if (variant === "destructive") {
        toast.error(message || title || "Erro")
      } else {
        toast(message || title || "Tudo certo")
      }
    },
  }
}
