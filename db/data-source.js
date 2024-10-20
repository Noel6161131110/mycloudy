import { DataSource } from 'typeorm';

export const AppDataSource = new DataSource({
    type: 'postgres',
    host: 'localhost',
    port: 5432,
    username: 'postgres',
    password: 'admin',
    database: 'mycloudy',
    synchronize: true, // Make sure tables are auto-created
    entities: [process.cwd() + '/models/*.js'], // Register entity
});