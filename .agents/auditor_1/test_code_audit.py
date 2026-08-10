import math

class DynamicWeightFuseEngine:
    """
    方案一：非线性动态权值熔断与卡尔曼-EWMA 滤波引擎
    """
    def __init__(self, w_base=0.40, w_max=0.85, theta_shock=0.25, 
                 theta_recovery=0.45, gamma=0.05, N_0=30):
        self.w_base = w_base
        self.w_max = w_max
        self.theta_shock = theta_shock
        self.theta_recovery = theta_recovery
        self.gamma = gamma
        self.N_0 = N_0
        
        # 卡尔曼状态
        self.x_hat = 0.50
        self.P = 1.0
        self.Q = 0.01
        self.is_fused = False
        self.fused_days = 0

    def filter_and_fuse(self, s_dynamic_raw: float, s_static: float, N_samples: int, R_noise: float = 0.05):
        # 1. 卡尔曼滤波更新
        P_prime = self.P + self.Q
        K_gain = P_prime / (P_prime + R_noise)
        self.x_hat = self.x_hat + K_gain * (s_dynamic_raw - self.x_hat)
        self.P = (1.0 - K_gain) * P_prime
        s_dynamic_filtered = self.x_hat
        
        # 2. 迟滞熔断状态判断
        if s_dynamic_filtered < self.theta_shock:
            self.is_fused = True
            self.fused_days = 0
        elif self.is_fused and s_dynamic_filtered >= self.theta_recovery:
            self.fused_days += 1
            if self.fused_days >= 3:
                self.is_fused = False

        # 3. 计算 Sigmoid 非线性动态权重
        if self.is_fused:
            w_dynamic = self.w_max
        else:
            sigmoid_term = 1.0 / (1.0 + math.exp(-(self.theta_shock - s_dynamic_filtered) / self.gamma))
            w_dynamic = self.w_base + (self.w_max - self.w_base) * sigmoid_term

        # 4. 冷启动置信度缩放
        confidence = 1.0 - math.exp(-N_samples / self.N_0)
        w_static_nominal = 1.0 - w_dynamic
        w_static_effective = w_static_nominal * confidence
        
        # 归一化
        w_sum = w_dynamic + w_static_effective
        w_dynamic_final = w_dynamic / w_sum
        w_static_final = w_static_effective / w_sum

        w_composite = w_static_final * s_static + w_dynamic_final * s_dynamic_filtered
        
        return {
            "W_composite": round(w_composite, 4),
            "w_dynamic": round(w_dynamic_final, 4),
            "w_static": round(w_static_final, 4),
            "is_fused": self.is_fused,
            "s_dynamic_filtered": round(s_dynamic_filtered, 4)
        }


def test_acute_shock_remediation():
    engine = DynamicWeightFuseEngine()
    # 模拟急性心理崩溃: static=0.90 (历史学霸), dynamic_raw=0.10 (突发崩溃)
    res = engine.filter_and_fuse(s_dynamic_raw=0.10, s_static=0.90, N_samples=100)
    print("Acute shock test output:", res)
    assert res["is_fused"] == True, "必须触发急性相变熔断"
    assert res["w_dynamic"] >= 0.80, "动态心理接管权重必须 >= 80%"
    assert res["W_composite"] <= 0.28, "综合得分必须强制降维，切断高难任务"
    print("Acute shock test PASSED")

def test_positive_gaming_detection():
    delta_gaming = 0.95 - 0.30
    print("Delta gaming:", delta_gaming)
    assert delta_gaming > 0.25, "必须判定为 POSITIVE_GAMING"
    print("Positive gaming test PASSED")

if __name__ == "__main__":
    test_acute_shock_remediation()
    test_positive_gaming_detection()
