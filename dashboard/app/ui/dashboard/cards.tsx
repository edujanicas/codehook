import {
  GlobeAltIcon,
  ServerIcon,
  CodeBracketIcon,
} from '@heroicons/react/24/outline';
import { roboto } from '@/app/ui/fonts';
import { fetchCardData } from '@/app/lib/data';

const iconMap = {
  events: GlobeAltIcon,
  providers: ServerIcon,
  endpoints: CodeBracketIcon,
};

export default async function CardWrapper() {
  const {
    numberOfEvents,
    numberOfProviders,
    numberOfEndpoints,
  } = await fetchCardData();
  
  return (
    <>
      <Card title="Total Events" value={numberOfEvents} type="events" />
      <Card title="Number of Providers" value={numberOfProviders} type="providers" />
      <Card title="Number of Endpoints" value={numberOfEndpoints} type="endpoints" />
    </>
  );
}

export function Card({
  title,
  value,
  type,
}: {
  title: string;
  value: number | string;
  type: 'endpoints' | 'providers' | 'events';
}) {
  const Icon = iconMap[type];

  return (
    <div className="rounded-xl bg-gray-50 p-2 shadow-sm">
      <div className="flex p-4">
        {Icon ? <Icon className="h-5 w-5 text-gray-700" /> : null}
        <h3 className="ml-2 text-sm font-medium">{title}</h3>
      </div>
      <p
        className={`${roboto.className}
          truncate rounded-xl bg-white px-4 py-8 text-center text-2xl`}
      >
        {value}
      </p>
    </div>
  );
}
