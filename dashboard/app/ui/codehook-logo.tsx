import Image from 'next/image'
import { CodeBracketIcon } from '@heroicons/react/24/outline';
import { roboto } from '@/app/ui/fonts';

export default function CodehookLogo() {
  return (
    <div
      className={`${roboto.className} flex flex-row items-center leading-none text-white`}
    >
      <Image
        src="/logo-alternate.png"
        width={500}
        height={500}
        alt="Logo of codehook.ai"
      />
    </div>
  );
}
