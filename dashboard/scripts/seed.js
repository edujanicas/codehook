const { db } = require('@vercel/postgres');
const {
  invoices,
  customers,
  users,
  endpoints,
  providers,
  events,
  event_history
} = require('../app/lib/placeholder-data.js');
const bcrypt = require('bcrypt');

async function seedUsers(client) {
  try {
    await client.sql`CREATE EXTENSION IF NOT EXISTS "uuid-ossp"`;
    // Create the "users" table if it doesn't exist
    const createTable = await client.sql`
      CREATE TABLE IF NOT EXISTS users (
        id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
      );
    `;

    console.log(`Created "users" table`);

    // Insert data into the "users" table
    const insertedUsers = await Promise.all(
      users.map(async (user) => {
        const hashedPassword = await bcrypt.hash(user.password, 10);
        return client.sql`
        INSERT INTO users (id, name, email, password)
        VALUES (${user.id}, ${user.name}, ${user.email}, ${hashedPassword})
        ON CONFLICT (id) DO NOTHING;
      `;
      }),
    );

    console.log(`Seeded ${insertedUsers.length} users`);

    return {
      createTable,
      users: insertedUsers,
    };
  } catch (error) {
    console.error('Error seeding users:', error);
    throw error;
  }
}

async function seedEndpoints(client) {
  try {
    // Create the "endpoints" table if it doesn't exist
    const createTable = await client.sql`
      CREATE TABLE IF NOT EXISTS endpoints (
        id VARCHAR(255) PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        api_id VARCHAR(255) NOT NULL,
        url TEXT NOT NULL
      );
    `;

    console.log(`Created "endpoints" table`);

    // Insert data into the "endpoints" table
    const insertedEndpoints = await Promise.all(
      endpoints.map(async (endpoint) => {
        return client.sql`
        INSERT INTO endpoints (id, name, api_id, url)
        VALUES (${endpoint.id}, ${endpoint.name}, ${endpoint.api_id}, ${endpoint.url})
        ON CONFLICT (id) DO NOTHING;
      `;
      }),
    );

    console.log(`Seeded ${insertedEndpoints.length} endpoints`);

    return {
      createTable,
      users: insertedEndpoints,
    };
  } catch (error) {
    console.error('Error seeding endpoints:', error);
    throw error;
  }
}

async function seedInvoices(client) {
  try {
    await client.sql`CREATE EXTENSION IF NOT EXISTS "uuid-ossp"`;

    // Create the "invoices" table if it doesn't exist
    const createTable = await client.sql`
    CREATE TABLE IF NOT EXISTS invoices (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    customer_id UUID NOT NULL,
    amount INT NOT NULL,
    status VARCHAR(255) NOT NULL,
    date DATE NOT NULL
  );
`;

    console.log(`Created "invoices" table`);

    // Insert data into the "invoices" table
    const insertedInvoices = await Promise.all(
      invoices.map(
        (invoice) => client.sql`
        INSERT INTO invoices (customer_id, amount, status, date)
        VALUES (${invoice.customer_id}, ${invoice.amount}, ${invoice.status}, ${invoice.date})
        ON CONFLICT (id) DO NOTHING;
      `,
      ),
    );

    console.log(`Seeded ${insertedInvoices.length} invoices`);

    return {
      createTable,
      invoices: insertedInvoices,
    };
  } catch (error) {
    console.error('Error seeding invoices:', error);
    throw error;
  }
}

async function seedProviders(client) {
  try {
    // Create the "providers" table if it doesn't exist
    const createTable = await client.sql`
      CREATE TABLE IF NOT EXISTS providers (
        we_id VARCHAR(255) PRIMARY KEY,
        source VARCHAR(255) NOT NULL,
        events VARCHAR(255) NOT NULL
      );
    `;

    console.log(`Created "providers" table`);

    // Insert data into the "endpoints" table
    const insertedProviders = await Promise.all(
      providers.map(async (provider) => {
        return client.sql`
        INSERT INTO providers (we_id, source, events)
        VALUES (${provider.we_id}, ${provider.source}, ${provider.events})
        ON CONFLICT (we_id) DO NOTHING;
      `;
      }),
    );

    console.log(`Seeded ${insertedProviders.length} providers`);

    return {
      createTable,
      users: insertedProviders,
    };
  } catch (error) {
    console.error('Error seeding providers:', error);
    throw error;
  }
}

async function seedCustomers(client) {
  try {
    await client.sql`CREATE EXTENSION IF NOT EXISTS "uuid-ossp"`;

    // Create the "customers" table if it doesn't exist
    const createTable = await client.sql`
      CREATE TABLE IF NOT EXISTS customers (
        id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL,
        image_url VARCHAR(255) NOT NULL
      );
    `;

    console.log(`Created "customers" table`);

    // Insert data into the "customers" table
    const insertedCustomers = await Promise.all(
      customers.map(
        (customer) => client.sql`
        INSERT INTO customers (id, name, email, image_url)
        VALUES (${customer.id}, ${customer.name}, ${customer.email}, ${customer.image_url})
        ON CONFLICT (id) DO NOTHING;
      `,
      ),
    );

    console.log(`Seeded ${insertedCustomers.length} customers`);

    return {
      createTable,
      customers: insertedCustomers,
    };
  } catch (error) {
    console.error('Error seeding customers:', error);
    throw error;
  }
}

async function seedEvents(client) {
  try {
    // Create the "providers" table if it doesn't exist
    const createTable = await client.sql`
      CREATE TABLE IF NOT EXISTS events (
        id VARCHAR(255) PRIMARY KEY,
        type VARCHAR(255) NOT NULL,
        provider VARCHAR(255) NOT NULL,
        payload JSON
      );
    `;

    console.log(`Created "events" table`);

    // Insert data into the "endpoints" table
    const insertedEvents = await Promise.all(
      events.map(async (event) => {
        return client.sql`
        INSERT INTO events (id, type, provider, payload)
        VALUES (${event.id}, ${event.type}, ${event.provider}, ${event.payload})
        ON CONFLICT (id) DO NOTHING;
      `;
      }),
    );

    console.log(`Seeded ${insertedEvents.length} events`);

    return {
      createTable,
      users: insertedEvents,
    };
  } catch (error) {
    console.error('Error seeding events:', error);
    throw error;
  }
}

async function seedEventHistory(client) {
  try {
    // Create the "event_history" table if it doesn't exist
    const createTable = await client.sql`
      CREATE TABLE IF NOT EXISTS event_history (
        month VARCHAR(4) NOT NULL UNIQUE,
        events INT NOT NULL
      );
    `;

    console.log(`Created "event_history" table`);

    // Insert data into the "revenue" table
    const insertedHistory = await Promise.all(
      event_history.map(
        (evt) => client.sql`
        INSERT INTO event_history (month, events)
        VALUES (${evt.month}, ${evt.events})
        ON CONFLICT (month) DO NOTHING;
      `,
      ),
    );

    console.log(`Seeded ${insertedHistory.length} event_history`);

    return {
      createTable,
      event_history: insertedHistory,
    };
  } catch (error) {
    console.error('Error seeding event_history:', error);
    throw error;
  }
}

async function main() {
  const client = await db.connect();

  await seedUsers(client);
  await seedCustomers(client);
  await seedInvoices(client);

  await seedEndpoints(client);
  await seedProviders(client);
  await seedEvents(client);
  await seedEventHistory(client);

  await client.end();
}

main().catch((err) => {
  console.error(
    'An error occurred while attempting to seed the database:',
    err,
  );
});
