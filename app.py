import streamlit as st
import numpy as np
import sympy as sp
import matplotlib.pyplot as plt

# إعدادات الصفحة
st.set_page_config(page_title="حاسبة التكامل", page_icon="🧮", layout="centered")

st.title("🧮 حاسبة التكامل العددي التفاعلية")
st.write("أدخل الدالة وحدد المعطيات لرؤية النتيجة والرسم البياني للمساحة تحت المنحنى.")

# --- واجهة المستخدم ---
func_input = st.text_input("الدالة f(x):", value="e^(-x^2)")

col1, col2 = st.columns(2)
with col1:
    a = st.number_input("الحد الأدنى (a):", value=0.0)
with col2:
    b_val = st.number_input("الحد الأقصى (b):", value=2.0)

method = st.selectbox("طريقة الحل:", [
    "شبه المنحرف (Trapezoidal)", 
    "سمبسون 1/3 (Simpson 1/3)", 
    "سمبسون 3/8 (Simpson 3/8)"
])

input_type = st.radio("المدخلات المتاحة:", ["عدد القطاعات (n)", "حجم الخطوة (h)"])
val = st.number_input("أدخل القيمة (n أو h):", value=4.0, min_value=0.0001)

# --- زر الحساب ---
if st.button("🚀 احسب وارسم", type="primary", use_container_width=True):
    func_str = func_input.replace('^', '**')
    
    if a >= b_val:
        st.error("❌ خطأ: الحد الأقصى يجب أن يكون أكبر من الحد الأدنى.")
    else:
        x = sp.Symbol('x')
        try:
            # تحضير الدالة
            f_expr = sp.sympify(func_str, locals={'e': sp.E})
            f = sp.lambdify(x, f_expr, "numpy")
            f(a) # اختبار سريع
            
            # حساب n و h
            if input_type == "حجم الخطوة (h)":
                h = val
                n_calc = (b_val - a) / h
                n = int(round(n_calc))
                if abs(n_calc - n) > 1e-6:
                    st.error(f"❌ خطأ: الخطوة h={h} لا تقسم المسافة بشكل صحيح.")
                    st.stop()
            else:
                n = int(val)
                h = (b_val - a) / n

            # التأكد من الشروط
            if "1/3" in method and n % 2 != 0:
                st.error(f"❌ خطأ: طريقة سمبسون 1/3 تتطلب (n) زوجياً، لكن المدخلات تعطي n = {n}")
                st.stop()
            elif "3/8" in method and n % 3 != 0:
                st.error(f"❌ خطأ: طريقة سمبسون 3/8 تتطلب (n) من مضاعفات 3، لكن المدخلات تعطي n = {n}")
                st.stop()

            # الحسابات
            x_vals = np.linspace(a, b_val, n + 1)
            y_vals = f(x_vals)
            if isinstance(y_vals, (int, float)):
                y_vals = np.full_like(x_vals, y_vals)

            if "شبه المنحرف" in method:
                result = (h / 2) * (y_vals[0] + 2 * np.sum(y_vals[1:-1]) + y_vals[-1])
            elif "1/3" in method:
                result = (h / 3) * (y_vals[0] + 4 * np.sum(y_vals[1:-1:2]) + 2 * np.sum(y_vals[2:-2:2]) + y_vals[-1])
            elif "3/8" in method:
                integral = y_vals[0] + y_vals[-1]
                for i in range(1, n):
                    if i % 3 == 0:
                        integral += 2 * y_vals[i]
                    else:
                        integral += 3 * y_vals[i]
                result = (3 * h / 8) * integral

            # طباعة النتيجة
            st.success("✅ تم الحساب بنجاح!")
            st.info(f"**النتيجة التقريبية = {float(result):.6f}** \n(عدد القطاعات: {n} | الخطوة: {h})")

            # الرسم البياني
            x_smooth = np.linspace(a, b_val, 500)
            y_smooth = f(x_smooth)
            if isinstance(y_smooth, (int, float)):
                y_smooth = np.full_like(x_smooth, y_smooth)

            fig, ax = plt.subplots(figsize=(8, 4))
            ax.plot(x_smooth, y_smooth, 'b-', linewidth=2, label=f'f(x) = {func_input}')
            
            if n <= 100:
                for i in range(n):
                    xs = [x_vals[i], x_vals[i], x_vals[i+1], x_vals[i+1]]
                    ys = [0, y_vals[i], y_vals[i+1], 0]
                    ax.fill(xs, ys, 'skyblue', edgecolor='black', alpha=0.5, linewidth=1)
            else:
                ax.fill_between(x_smooth, 0, y_smooth, color='skyblue', alpha=0.5)

            ax.axhline(0, color='black', linewidth=1)
            ax.set_title(f"Numerical Integration ({method})", fontsize=12)
            ax.legend()
            ax.grid(True, linestyle='--', alpha=0.6)
            
            # عرض الرسمة في التطبيق
            st.pyplot(fig)

        except Exception as e:
            st.error("❌ خطأ: الدالة مكتوبة بشكل خاطئ أو تحتوي على رموز مجهولة. تأكد من استخدام المتغير x.")
