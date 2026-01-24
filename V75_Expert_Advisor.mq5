//+------------------------------------------------------------------+
//|                                        V75_Expert_Advisor.mq5    |
//|                        Volatility Index 75 Expert Advisor        |
//|                           Multi-Strategy Trading System          |
//+------------------------------------------------------------------+
#property copyright "Trading Bot EA System"
#property link      "https://github.com/BasJunior/Trading-bot"
#property version   "1.00"
#property description "V75 Expert Advisor with Multiple Strategies"
#property description "EMA Crossover, RSI Reversal, Bollinger Breakout, MACD Momentum"

//--- Input Parameters
//+------------------------------------------------------------------+
//| Core Trading Parameters                                          |
//+------------------------------------------------------------------+
input group "=== Core Trading Parameters ==="
input double   InpLotSize = 0.01;              // Lot Size
input double   InpMinLotSize = 0.01;           // Minimum Lot Size
input double   InpMaxLotSize = 10.0;           // Maximum Lot Size

//+------------------------------------------------------------------+
//| Risk Management Parameters                                       |
//+------------------------------------------------------------------+
input group "=== Risk Management ==="
input double   InpStopLossPips = 50.0;         // Stop Loss (pips)
input double   InpTakeProfitPips = 100.0;      // Take Profit (pips)
input double   InpRiskPerTrade = 2.0;          // Risk Per Trade (%)
input double   InpMaxDailyLoss = 5.0;          // Max Daily Loss (%)
input double   InpMaxDrawdown = 10.0;          // Max Drawdown (%)
input double   InpTrailingStopPips = 30.0;     // Trailing Stop (pips)
input bool     InpUseTrailingStop = true;      // Enable Trailing Stop

//+------------------------------------------------------------------+
//| Position Management                                              |
//+------------------------------------------------------------------+
input group "=== Position Management ==="
input int      InpMaxOpenTrades = 3;           // Max Open Trades
input int      InpMaxTradesPerHour = 10;       // Max Trades Per Hour
input int      InpCooldownAfterLoss = 60;      // Cooldown After Loss (seconds)

//+------------------------------------------------------------------+
//| Strategy Parameters                                              |
//+------------------------------------------------------------------+
input group "=== EMA Strategy ==="
input int      InpEMAFast = 9;                 // EMA Fast Period
input int      InpEMASlow = 21;                // EMA Slow Period

input group "=== RSI Strategy ==="
input int      InpRSIPeriod = 14;              // RSI Period
input double   InpRSIOverbought = 70.0;        // RSI Overbought Level
input double   InpRSIOversold = 30.0;          // RSI Oversold Level

input group "=== Bollinger Bands Strategy ==="
input int      InpBBPeriod = 20;               // Bollinger Period
input double   InpBBDeviation = 2.0;           // Bollinger Deviation

input group "=== MACD Strategy ==="
input int      InpMACDFast = 12;               // MACD Fast Period
input int      InpMACDSlow = 26;               // MACD Slow Period
input int      InpMACDSignal = 9;              // MACD Signal Period

input group "=== V75 Specific ==="
input double   InpVolatilityThreshold = 0.02;  // Volatility Threshold
input int      InpBreakoutLookback = 20;       // Breakout Lookback Candles
input double   InpMomentumThreshold = 0.5;     // Momentum Threshold

input group "=== General Settings ==="
input int      InpMagicNumber = 75001;         // Magic Number
input string   InpTradeComment = "V75_EA";     // Trade Comment
input bool     InpEnableDetailedLog = false;   // Enable Detailed Logging

//--- Global Variables
int handleEMAFast, handleEMASlow;
int handleRSI;
int handleBBands;
int handleMACDMain, handleMACDSignal;
int handleATR;

double emaFastBuffer[], emaSlowBuffer[];
double rsiBuffer[];
double bbUpperBuffer[], bbMiddleBuffer[], bbLowerBuffer[];
double macdMainBuffer[], macdSignalBuffer[];
double atrBuffer[];

datetime lastTradeTime = 0;
datetime lastLossTime = 0;
datetime hourStartTime = 0;
int tradesThisHour = 0;

double startingBalance = 0;
double dailyProfit = 0;
double dailyLoss = 0;
datetime dayStartTime = 0;

// Statistics
int totalTrades = 0;
int winningTrades = 0;
int losingTrades = 0;
double totalProfit = 0;
double totalLoss = 0;
double maxDrawdown = 0;

// Market Condition
enum ENUM_MARKET_CONDITION {
   MARKET_TRENDING_UP,
   MARKET_TRENDING_DOWN,
   MARKET_RANGING,
   MARKET_HIGH_VOLATILITY,
   MARKET_LOW_VOLATILITY,
   MARKET_BREAKOUT
};

ENUM_MARKET_CONDITION currentMarketCondition = MARKET_RANGING;

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
   // Set magic number for this EA
   if(InpMagicNumber <= 0) {
      Print("ERROR: Magic number must be positive");
      return INIT_PARAMETERS_INCORRECT;
   }
   
   // Validate lot sizes
   if(InpLotSize < InpMinLotSize || InpLotSize > InpMaxLotSize) {
      Print("ERROR: Lot size must be between ", InpMinLotSize, " and ", InpMaxLotSize);
      return INIT_PARAMETERS_INCORRECT;
   }
   
   // Validate risk parameters
   if(InpRiskPerTrade <= 0 || InpRiskPerTrade > 10) {
      Print("ERROR: Risk per trade must be between 0 and 10 percent");
      return INIT_PARAMETERS_INCORRECT;
   }
   
   if(InpStopLossPips <= 0 || InpTakeProfitPips <= 0) {
      Print("ERROR: Stop Loss and Take Profit must be positive");
      return INIT_PARAMETERS_INCORRECT;
   }
   
   // Initialize indicators
   handleEMAFast = iMA(_Symbol, PERIOD_CURRENT, InpEMAFast, 0, MODE_EMA, PRICE_CLOSE);
   handleEMASlow = iMA(_Symbol, PERIOD_CURRENT, InpEMASlow, 0, MODE_EMA, PRICE_CLOSE);
   handleRSI = iRSI(_Symbol, PERIOD_CURRENT, InpRSIPeriod, PRICE_CLOSE);
   handleBBands = iBands(_Symbol, PERIOD_CURRENT, InpBBPeriod, 0, InpBBDeviation, PRICE_CLOSE);
   handleMACDMain = iMACD(_Symbol, PERIOD_CURRENT, InpMACDFast, InpMACDSlow, InpMACDSignal, PRICE_CLOSE);
   handleATR = iATR(_Symbol, PERIOD_CURRENT, 14);
   
   // Check if indicators are created successfully
   if(handleEMAFast == INVALID_HANDLE || handleEMASlow == INVALID_HANDLE ||
      handleRSI == INVALID_HANDLE || handleBBands == INVALID_HANDLE ||
      handleMACDMain == INVALID_HANDLE || handleATR == INVALID_HANDLE) {
      Print("ERROR: Failed to create indicator handles");
      return INIT_FAILED;
   }
   
   // Initialize arrays
   ArraySetAsSeries(emaFastBuffer, true);
   ArraySetAsSeries(emaSlowBuffer, true);
   ArraySetAsSeries(rsiBuffer, true);
   ArraySetAsSeries(bbUpperBuffer, true);
   ArraySetAsSeries(bbMiddleBuffer, true);
   ArraySetAsSeries(bbLowerBuffer, true);
   ArraySetAsSeries(macdMainBuffer, true);
   ArraySetAsSeries(macdSignalBuffer, true);
   ArraySetAsSeries(atrBuffer, true);
   
   // Initialize time tracking
   startingBalance = AccountInfoDouble(ACCOUNT_BALANCE);
   dayStartTime = TimeCurrent();
   hourStartTime = TimeCurrent();
   
   Print("=== V75 Expert Advisor Initialized ===");
   Print("Symbol: ", _Symbol);
   Print("Lot Size: ", InpLotSize);
   Print("Stop Loss: ", InpStopLossPips, " pips");
   Print("Take Profit: ", InpTakeProfitPips, " pips");
   Print("Max Open Trades: ", InpMaxOpenTrades);
   Print("Magic Number: ", InpMagicNumber);
   
   return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   // Release indicator handles
   if(handleEMAFast != INVALID_HANDLE) IndicatorRelease(handleEMAFast);
   if(handleEMASlow != INVALID_HANDLE) IndicatorRelease(handleEMASlow);
   if(handleRSI != INVALID_HANDLE) IndicatorRelease(handleRSI);
   if(handleBBands != INVALID_HANDLE) IndicatorRelease(handleBBands);
   if(handleMACDMain != INVALID_HANDLE) IndicatorRelease(handleMACDMain);
   if(handleATR != INVALID_HANDLE) IndicatorRelease(handleATR);
   
   // Print statistics
   Print("=== V75 EA Statistics ===");
   Print("Total Trades: ", totalTrades);
   Print("Winning Trades: ", winningTrades);
   Print("Losing Trades: ", losingTrades);
   Print("Win Rate: ", (totalTrades > 0 ? (winningTrades * 100.0 / totalTrades) : 0), "%");
   Print("Total Profit: ", totalProfit);
   Print("Total Loss: ", totalLoss);
   Print("Net Profit: ", totalProfit - MathAbs(totalLoss));
   Print("Max Drawdown: ", maxDrawdown, "%");
   
   Print("V75 Expert Advisor Deinitialized. Reason: ", reason);
}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
{
   // Check if new bar
   static datetime lastBarTime = 0;
   datetime currentBarTime = iTime(_Symbol, PERIOD_CURRENT, 0);
   
   if(currentBarTime == lastBarTime) {
      // Process trailing stops on every tick
      if(InpUseTrailingStop) {
         ProcessTrailingStops();
      }
      return;
   }
   
   lastBarTime = currentBarTime;
   
   // Update daily stats if new day
   if(TimeCurrent() - dayStartTime >= 86400) {
      ResetDailyStats();
   }
   
   // Update hourly trade counter
   if(TimeCurrent() - hourStartTime >= 3600) {
      tradesThisHour = 0;
      hourStartTime = TimeCurrent();
   }
   
   // Check risk limits
   if(!CheckRiskLimits()) {
      if(InpEnableDetailedLog) Print("Risk limits exceeded, not trading");
      return;
   }
   
   // Check rate limits
   if(!CheckRateLimits()) {
      if(InpEnableDetailedLog) Print("Rate limits exceeded, not trading");
      return;
   }
   
   // Update indicators
   if(!UpdateIndicators()) {
      if(InpEnableDetailedLog) Print("Failed to update indicators");
      return;
   }
   
   // Update market condition
   UpdateMarketCondition();
   
   // Check for trading signals
   CheckTradingSignals();
   
   // Process trailing stops
   if(InpUseTrailingStop) {
      ProcessTrailingStops();
   }
}

//+------------------------------------------------------------------+
//| Update indicator buffers                                         |
//+------------------------------------------------------------------+
bool UpdateIndicators()
{
   // Copy indicator data
   if(CopyBuffer(handleEMAFast, 0, 0, 3, emaFastBuffer) <= 0) return false;
   if(CopyBuffer(handleEMASlow, 0, 0, 3, emaSlowBuffer) <= 0) return false;
   if(CopyBuffer(handleRSI, 0, 0, 3, rsiBuffer) <= 0) return false;
   if(CopyBuffer(handleBBands, 0, 0, 3, bbUpperBuffer) <= 0) return false;
   if(CopyBuffer(handleBBands, 1, 0, 3, bbMiddleBuffer) <= 0) return false;
   if(CopyBuffer(handleBBands, 2, 0, 3, bbLowerBuffer) <= 0) return false;
   if(CopyBuffer(handleMACDMain, 0, 0, 3, macdMainBuffer) <= 0) return false;
   if(CopyBuffer(handleMACDMain, 1, 0, 3, macdSignalBuffer) <= 0) return false;
   if(CopyBuffer(handleATR, 0, 0, 3, atrBuffer) <= 0) return false;
   
   return true;
}

//+------------------------------------------------------------------+
//| Update market condition                                          |
//+------------------------------------------------------------------+
void UpdateMarketCondition()
{
   double emaFast = emaFastBuffer[0];
   double emaSlow = emaSlowBuffer[0];
   
   // Trend detection
   bool trendingUp = emaFast > emaSlow * 1.001;
   bool trendingDown = emaFast < emaSlow * 0.999;
   
   // Volatility detection
   double atr = atrBuffer[0];
   double price = iClose(_Symbol, PERIOD_CURRENT, 0);
   double volatility = atr / price;
   
   if(volatility > InpVolatilityThreshold * 2) {
      currentMarketCondition = MARKET_HIGH_VOLATILITY;
   }
   else if(volatility < InpVolatilityThreshold * 0.5) {
      currentMarketCondition = MARKET_LOW_VOLATILITY;
   }
   else if(trendingUp) {
      currentMarketCondition = MARKET_TRENDING_UP;
   }
   else if(trendingDown) {
      currentMarketCondition = MARKET_TRENDING_DOWN;
   }
   else {
      currentMarketCondition = MARKET_RANGING;
   }
}

//+------------------------------------------------------------------+
//| Check risk limits                                                |
//+------------------------------------------------------------------+
bool CheckRiskLimits()
{
   // Check daily loss limit
   double currentBalance = AccountInfoDouble(ACCOUNT_BALANCE);
   double dailyLossPercent = 0;
   if(startingBalance > 0) {
      dailyLossPercent = (MathAbs(dailyLoss) / startingBalance) * 100;
   }
   
   if(dailyLossPercent >= InpMaxDailyLoss) {
      if(InpEnableDetailedLog) Print("Daily loss limit reached: ", dailyLossPercent, "%");
      return false;
   }
   
   // Check max drawdown
   double drawdown = 0;
   if(startingBalance > 0) {
      drawdown = ((startingBalance - currentBalance) / startingBalance) * 100;
   }
   
   if(drawdown >= InpMaxDrawdown) {
      if(InpEnableDetailedLog) Print("Max drawdown reached: ", drawdown, "%");
      return false;
   }
   
   // Check max open trades
   int openTrades = CountOpenTrades();
   if(openTrades >= InpMaxOpenTrades) {
      if(InpEnableDetailedLog) Print("Max open trades reached: ", openTrades);
      return false;
   }
   
   return true;
}

//+------------------------------------------------------------------+
//| Check rate limits                                                |
//+------------------------------------------------------------------+
bool CheckRateLimits()
{
   // Check hourly trade limit
   if(tradesThisHour >= InpMaxTradesPerHour) {
      if(InpEnableDetailedLog) Print("Hourly trade limit reached");
      return false;
   }
   
   // Check cooldown after loss
   if(lastLossTime > 0) {
      if(TimeCurrent() - lastLossTime < InpCooldownAfterLoss) {
         if(InpEnableDetailedLog) Print("In cooldown period after loss");
         return false;
      }
   }
   
   return true;
}

//+------------------------------------------------------------------+
//| Check trading signals                                            |
//+------------------------------------------------------------------+
void CheckTradingSignals()
{
   int signalCount = 0;
   int buySignals = 0;
   int sellSignals = 0;
   
   // EMA Crossover Strategy
   if(CheckEMACrossover() == 1) buySignals++;
   else if(CheckEMACrossover() == -1) sellSignals++;
   
   // RSI Reversal Strategy
   if(CheckRSIReversal() == 1) buySignals++;
   else if(CheckRSIReversal() == -1) sellSignals++;
   
   // Bollinger Breakout Strategy
   if(CheckBollingerBreakout() == 1) buySignals++;
   else if(CheckBollingerBreakout() == -1) sellSignals++;
   
   // MACD Momentum Strategy
   if(CheckMACDMomentum() == 1) buySignals++;
   else if(CheckMACDMomentum() == -1) sellSignals++;
   
   // Combined Strategy: Require at least 2 confirming signals
   if(buySignals >= 2) {
      OpenTrade(ORDER_TYPE_BUY, "Combined Strategy: " + IntegerToString(buySignals) + " buy signals");
   }
   else if(sellSignals >= 2) {
      OpenTrade(ORDER_TYPE_SELL, "Combined Strategy: " + IntegerToString(sellSignals) + " sell signals");
   }
}

//+------------------------------------------------------------------+
//| EMA Crossover Strategy                                           |
//+------------------------------------------------------------------+
int CheckEMACrossover()
{
   double emaFastCurrent = emaFastBuffer[0];
   double emaFastPrev = emaFastBuffer[1];
   double emaSlowCurrent = emaSlowBuffer[0];
   double emaSlowPrev = emaSlowBuffer[1];
   
   // Bullish crossover
   if(emaFastPrev <= emaSlowPrev && emaFastCurrent > emaSlowCurrent) {
      if(InpEnableDetailedLog) Print("EMA Bullish Crossover detected");
      return 1;
   }
   
   // Bearish crossover
   if(emaFastPrev >= emaSlowPrev && emaFastCurrent < emaSlowCurrent) {
      if(InpEnableDetailedLog) Print("EMA Bearish Crossover detected");
      return -1;
   }
   
   return 0;
}

//+------------------------------------------------------------------+
//| RSI Reversal Strategy                                            |
//+------------------------------------------------------------------+
int CheckRSIReversal()
{
   double rsiCurrent = rsiBuffer[0];
   double rsiPrev = rsiBuffer[1];
   
   // RSI exiting oversold - potential buy
   if(rsiPrev < InpRSIOversold && rsiCurrent >= InpRSIOversold) {
      if(InpEnableDetailedLog) Print("RSI Reversal: Exiting oversold at ", rsiCurrent);
      return 1;
   }
   
   // RSI exiting overbought - potential sell
   if(rsiPrev > InpRSIOverbought && rsiCurrent <= InpRSIOverbought) {
      if(InpEnableDetailedLog) Print("RSI Reversal: Exiting overbought at ", rsiCurrent);
      return -1;
   }
   
   return 0;
}

//+------------------------------------------------------------------+
//| Bollinger Breakout Strategy                                      |
//+------------------------------------------------------------------+
int CheckBollingerBreakout()
{
   double price = iClose(_Symbol, PERIOD_CURRENT, 0);
   double pricePrev = iClose(_Symbol, PERIOD_CURRENT, 1);
   double upperBand = bbUpperBuffer[0];
   double lowerBand = bbLowerBuffer[0];
   double upperBandPrev = bbUpperBuffer[1];
   double lowerBandPrev = bbLowerBuffer[1];
   
   // Calculate momentum
   double momentum = 0;
   if(ArraySize(emaFastBuffer) >= 6) {
      double priceDiff = price - iClose(_Symbol, PERIOD_CURRENT, 5);
      double avgPrice = (price + iClose(_Symbol, PERIOD_CURRENT, 5)) / 2;
      if(avgPrice > 0) momentum = (priceDiff / avgPrice) * 100;
   }
   
   // Bullish breakout
   if(pricePrev < upperBandPrev && price > upperBand && momentum > 0) {
      if(InpEnableDetailedLog) Print("Bollinger Bullish Breakout detected");
      return 1;
   }
   
   // Bearish breakout
   if(pricePrev > lowerBandPrev && price < lowerBand && momentum < 0) {
      if(InpEnableDetailedLog) Print("Bollinger Bearish Breakout detected");
      return -1;
   }
   
   return 0;
}

//+------------------------------------------------------------------+
//| MACD Momentum Strategy                                           |
//+------------------------------------------------------------------+
int CheckMACDMomentum()
{
   double macdCurrent = macdMainBuffer[0];
   double macdPrev = macdMainBuffer[1];
   double signalCurrent = macdSignalBuffer[0];
   double signalPrev = macdSignalBuffer[1];
   double histogramCurrent = macdCurrent - signalCurrent;
   
   // Bullish crossover with positive histogram
   if(macdPrev <= signalPrev && macdCurrent > signalCurrent && histogramCurrent > 0) {
      if(InpEnableDetailedLog) Print("MACD Bullish Momentum detected");
      return 1;
   }
   
   // Bearish crossover with negative histogram
   if(macdPrev >= signalPrev && macdCurrent < signalCurrent && histogramCurrent < 0) {
      if(InpEnableDetailedLog) Print("MACD Bearish Momentum detected");
      return -1;
   }
   
   return 0;
}

//+------------------------------------------------------------------+
//| Open a trade                                                     |
//+------------------------------------------------------------------+
void OpenTrade(ENUM_ORDER_TYPE orderType, string reason)
{
   // Get current price
   double price = (orderType == ORDER_TYPE_BUY) ? SymbolInfoDouble(_Symbol, SYMBOL_ASK) : SymbolInfoDouble(_Symbol, SYMBOL_BID);
   
   // Calculate SL and TP
   double point = SymbolInfoDouble(_Symbol, SYMBOL_POINT);
   double digits = (int)SymbolInfoInteger(_Symbol, SYMBOL_DIGITS);
   
   double sl = 0, tp = 0;
   
   if(orderType == ORDER_TYPE_BUY) {
      sl = NormalizeDouble(price - InpStopLossPips * point * 10, digits);
      tp = NormalizeDouble(price + InpTakeProfitPips * point * 10, digits);
   }
   else {
      sl = NormalizeDouble(price + InpStopLossPips * point * 10, digits);
      tp = NormalizeDouble(price - InpTakeProfitPips * point * 10, digits);
   }
   
   // Prepare trade request
   MqlTradeRequest request = {};
   MqlTradeResult result = {};
   
   request.action = TRADE_ACTION_DEAL;
   request.symbol = _Symbol;
   request.volume = InpLotSize;
   request.type = orderType;
   request.price = price;
   request.sl = sl;
   request.tp = tp;
   request.deviation = 10;
   request.magic = InpMagicNumber;
   request.comment = InpTradeComment + " - " + reason;
   request.type_filling = ORDER_FILLING_IOC;
   
   // Send order
   if(!OrderSend(request, result)) {
      Print("ERROR: Failed to open trade. Error: ", GetLastError());
      return;
   }
   
   if(result.retcode != TRADE_RETCODE_DONE) {
      Print("ERROR: Trade rejected. Return code: ", result.retcode);
      return;
   }
   
   // Update statistics
   totalTrades++;
   tradesThisHour++;
   lastTradeTime = TimeCurrent();
   
   Print("=== Trade Opened ===");
   Print("Type: ", (orderType == ORDER_TYPE_BUY ? "BUY" : "SELL"));
   Print("Price: ", price);
   Print("SL: ", sl);
   Print("TP: ", tp);
   Print("Reason: ", reason);
   Print("Ticket: ", result.order);
}

//+------------------------------------------------------------------+
//| Process trailing stops                                           |
//+------------------------------------------------------------------+
void ProcessTrailingStops()
{
   double point = SymbolInfoDouble(_Symbol, SYMBOL_POINT);
   double digits = (int)SymbolInfoInteger(_Symbol, SYMBOL_DIGITS);
   double trailDistance = InpTrailingStopPips * point * 10;
   
   for(int i = PositionsTotal() - 1; i >= 0; i--) {
      if(PositionSelectByTicket(PositionGetTicket(i))) {
         if(PositionGetInteger(POSITION_MAGIC) != InpMagicNumber) continue;
         if(PositionGetString(POSITION_SYMBOL) != _Symbol) continue;
         
         double positionOpenPrice = PositionGetDouble(POSITION_PRICE_OPEN);
         double currentSL = PositionGetDouble(POSITION_SL);
         double currentPrice = PositionGetDouble(POSITION_PRICE_CURRENT);
         ENUM_POSITION_TYPE posType = (ENUM_POSITION_TYPE)PositionGetInteger(POSITION_TYPE);
         
         double newSL = 0;
         bool modifyNeeded = false;
         
         if(posType == POSITION_TYPE_BUY) {
            newSL = NormalizeDouble(currentPrice - trailDistance, digits);
            if(newSL > currentSL && newSL < currentPrice) {
               modifyNeeded = true;
            }
         }
         else if(posType == POSITION_TYPE_SELL) {
            newSL = NormalizeDouble(currentPrice + trailDistance, digits);
            if((currentSL == 0 || newSL < currentSL) && newSL > currentPrice) {
               modifyNeeded = true;
            }
         }
         
         if(modifyNeeded) {
            MqlTradeRequest request = {};
            MqlTradeResult result = {};
            
            request.action = TRADE_ACTION_SLTP;
            request.position = PositionGetTicket(i);
            request.symbol = _Symbol;
            request.sl = newSL;
            request.tp = PositionGetDouble(POSITION_TP);
            
            if(!OrderSend(request, result)) {
               Print("ERROR: Failed to modify trailing stop. Error: ", GetLastError());
            }
            else if(InpEnableDetailedLog) {
               Print("Trailing stop updated to ", newSL);
            }
         }
      }
   }
}

//+------------------------------------------------------------------+
//| Count open trades for this EA                                    |
//+------------------------------------------------------------------+
int CountOpenTrades()
{
   int count = 0;
   for(int i = 0; i < PositionsTotal(); i++) {
      if(PositionSelectByTicket(PositionGetTicket(i))) {
         if(PositionGetInteger(POSITION_MAGIC) == InpMagicNumber &&
            PositionGetString(POSITION_SYMBOL) == _Symbol) {
            count++;
         }
      }
   }
   return count;
}

//+------------------------------------------------------------------+
//| Reset daily statistics                                           |
//+------------------------------------------------------------------+
void ResetDailyStats()
{
   dailyProfit = 0;
   dailyLoss = 0;
   dayStartTime = TimeCurrent();
   
   if(InpEnableDetailedLog) Print("Daily statistics reset");
}

//+------------------------------------------------------------------+
//| Trade event handler                                              |
//+------------------------------------------------------------------+
void OnTrade()
{
   // Update statistics when trades close
   UpdateTradeStatistics();
}

//+------------------------------------------------------------------+
//| Update trade statistics                                          |
//+------------------------------------------------------------------+
void UpdateTradeStatistics()
{
   // Check closed positions in history
   HistorySelect(0, TimeCurrent());
   
   for(int i = HistoryDealsTotal() - 1; i >= 0; i--) {
      ulong ticket = HistoryDealGetTicket(i);
      if(ticket > 0) {
         if(HistoryDealGetInteger(ticket, DEAL_MAGIC) == InpMagicNumber &&
            HistoryDealGetString(ticket, DEAL_SYMBOL) == _Symbol) {
            
            double profit = HistoryDealGetDouble(ticket, DEAL_PROFIT);
            
            if(profit > 0) {
               winningTrades++;
               totalProfit += profit;
               dailyProfit += profit;
            }
            else if(profit < 0) {
               losingTrades++;
               totalLoss += profit;
               dailyLoss += profit;
               lastLossTime = TimeCurrent();
            }
            
            // Update max drawdown
            double currentBalance = AccountInfoDouble(ACCOUNT_BALANCE);
            if(startingBalance > 0) {
               double drawdown = ((startingBalance - currentBalance) / startingBalance) * 100;
               if(drawdown > maxDrawdown) {
                  maxDrawdown = drawdown;
               }
            }
         }
      }
   }
}

//+------------------------------------------------------------------+
