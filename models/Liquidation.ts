import { Model, DataTypes } from "sequelize";
import db from "../db";

interface ILiquidation {
  id?: number;
  symbol: string;
  side: string;
  volume: string;
  quantity: string;
  time: string;
}

class Liquidation extends Model<ILiquidation> {
  public id!: number;
  public symbol!: string;
  public side!: string;
  public volume!: string;
  public quatity!: string;
  public time!: string;
}

Liquidation.init(
  {
    id: {
      type: DataTypes.INTEGER,
      allowNull: false,
      primaryKey: true,
      autoIncrement: true,
    },
    symbol: DataTypes.STRING,
    side: DataTypes.STRING,
    volume: DataTypes.STRING,
    quantity: DataTypes.STRING,
    time: DataTypes.STRING,
  },
  {
    sequelize: db,
    modelName: "liquidation",
    timestamps: false,
  }
);

export default Liquidation;
