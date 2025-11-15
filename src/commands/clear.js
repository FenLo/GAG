const { SlashCommandBuilder, PermissionFlagsBits } = require('discord.js');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('clear')
        .setDescription('Sohbeti silmenize yarar.')
        .addIntegerOption(option =>
            option.setName('amount')
                .setDescription('Silinecek mesaj sayısı')
                .setRequired(true)
                .setMinValue(1)
                .setMaxValue(100))
        .setDefaultMemberPermissions(PermissionFlagsBits.Administrator),
    async execute(interaction) {
        const amount = interaction.options.getInteger('amount');

        try {
            const messages = await interaction.channel.messages.fetch({ limit: amount });
            await interaction.channel.bulkDelete(messages, true);
            
            const reply = await interaction.reply({ 
                content: `✅ ${messages.size} mesaj silindi.`,
                ephemeral: true 
            });
            
            setTimeout(() => reply.delete().catch(() => {}), 5000);
        } catch (error) {
            console.error('Clear error:', error);
            await interaction.reply({ 
                content: '❌ Mesajları silerken bir hata oluştu. (14 günden eski mesajlar silinemez)',
                ephemeral: true 
            });
        }
    }
};
