import { toast } from 'sonner';

export const showToast = {
  success: (message: string) => {
    toast.success(message, {
      duration: 3000,
      position: 'top-center',
    });
  },
  error: (message: string) => {
    toast.error(message, {
      duration: 5000,
      position: 'top-center',
    });
  },
  info: (message: string) => {
    toast.info(message, {
      duration: 3000,
      position: 'top-center',
    });
  },
};
