'use client';

import {
  CogIcon,
  WindowIcon,
  CodeBracketIcon,
} from '@heroicons/react/24/outline';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import clsx from 'clsx';

// Map of links to display in the side navigation.
// Depending on the size of the application, this would be stored in a database.
const links = [
  { name: 'Dashboard', href: '/dashboard', icon: WindowIcon },
  {
    name: 'Endpoints',
    href: '/dashboard/invoices',
    icon: CodeBracketIcon,
  },
  { name: 'Settings', href: '/dashboard/customers', icon: CogIcon },
];

export default function NavLinks() {
  const pathname = usePathname();
  return (
    <>
      {links.map((link) => {
        const LinkIcon = link.icon;
        return (
          <Link
            key={link.name}
            href={link.href}
            className={clsx(
              'flex h-[48px] grow items-center justify-center gap-2 rounded-md bg-gray-50 p-3 text-sm font-medium hover:bg-codehook-300 md:flex-none md:justify-start md:p-2 md:px-3',
              {
                'bg-codehook-900 text-white hover:bg-codehook-900 hover:text-white': pathname === link.href,
              },
            )}
          >
            <LinkIcon className="w-6" />
            <p className="hidden md:block">{link.name}</p>
          </Link>
        );
      })}
    </>
  );
}
