import { Model, DataTypes } from "sequelize";
import db from "../db";

interface IOrder {
  id?: number;
  pair: string;
  side: string;
  strength: number;
  price: number;
  distance: number;
  time: number;
}

class Order extends Model<IOrder> {
  public id!: number;
  public pair!: string;
  public side!: string;
  public strength!: number;
  public price!: number;
  public distance!: number;
  public time!: number;
}
Order.init(
  {
    id: {
      type: DataTypes.INTEGER,
      allowNull: false,
      primaryKey: true,
      autoIncrement: true,
    },
    pair: DataTypes.STRING,
    side: DataTypes.STRING,
    strength: DataTypes.INTEGER,
    price: DataTypes.FLOAT,
    distance: DataTypes.FLOAT,
    time: DataTypes.INTEGER,
  },
  {
    sequelize: db,
    modelName: "order",
    timestamps:false,
  }
);

// Order.afterCreate(async (order: any, options: any) => {
//   console.log("AFTER CREATE HOOK FIRED")
//   try {
//     const updatedEntries = await Order.findAll();
//     io.emit("databaseChange", updatedEntries);
//     console.log("New entry created. Updated entries emitted:", updatedEntries);
//   } catch (error) {
//     console.log("Error in the afterCreate hook:", error);
//   }
// });

// Order.afterDestroy(async (order: any, options: any) => {
//   console.log("AFTER DESTROY HOOK FIRED")
//   try {
//     const updatedEntries = await Order.findAll();
//     io.emit("databaseChange", updatedEntries);
//     console.log("Entry deleted. Updated entries emitted:", updatedEntries);
//   } catch (error) {
//     console.log("Error in the afterDestroy hook:", error);
//   }
// });


export default Order;
