import { EntitySchema } from 'typeorm';

export const FileModel = new EntitySchema({
  name: 'FileModel',
  tableName: 'FileModel', // Optionally specify the table name
  columns: {
    id: {
      type: 'int',
      primary: true,
      generated: true,
    },
    filename: {
      type: 'varchar',
    },
    fileExtension: {
      type: 'varchar',
    },
    filePath: {
      type: 'varchar',
    },
    fileType: {
      type: 'varchar',
    },
    totalLength: {
        type: 'float',
        nullable: true,
    },
    currentTrackAt: {
        type: 'float',
        nullable: true,
    },
    uploadedAt: {
      type: 'timestamp',
      createDate: true,
    },
  },
});